document.addEventListener("DOMContentLoaded", function () {
  const dropArea = document.getElementById("drop-area");
  const fileInput = document.getElementById("fileElem");
  const preview = document.getElementById("preview");
  const browseButton = document.getElementById("browseButton");
  const removeButton = document.querySelector(".remove-image");

  const form = document.getElementById("projectForm");
  const titleInput = document.querySelector("input[name='title']");
  const descriptionInput = document.querySelector(
    "textarea[name='description']"
  );
  const githubLinkInput = document.querySelector("input[name='github_link']");
  const techStackInput = document.querySelector("input[name='tech_stack']");
  const submitButton = document.getElementById("submitButton");

  const charCounter = document.querySelector(".char-counter");
  const charCount = document.getElementById("char-count");
  const charMax = document.getElementById("char-max");
  const MAX_CHARS = 500;
  charMax.textContent = MAX_CHARS;

  const techPillsContainer = document.getElementById("tech-pills-container");

  const repoPreview = document.getElementById("repo-preview");
  const repoName = document.getElementById("repo-name");
  const repoStars = document.getElementById("repo-stars");
  const repoForks = document.getElementById("repo-forks");
  const repoUpdated = document.getElementById("repo-updated");
  const repoDescription = document.getElementById("repo-description");

  const readmePreviewContainer = document.querySelector(
    ".readme-preview-container"
  );
  const readmeContent = document.getElementById("readme-content");
  const readmePlaceholder = document.getElementById("readme-placeholder");
  const readmeMarkdown = document.getElementById("readme-markdown");
  const readmeLoading = document.getElementById("readme-loading");

  const style = document.createElement("style");
  style.textContent = `
    .repo-preview.error {
      background-color: #fff8f8;
      border-color: #dc3545;
    }
    .repo-preview.error .repo-description {
      color: #dc3545;
    }
  `;
  document.head.appendChild(style);

  readmePreviewContainer.style.display = "none";
  submitButton.disabled = true;

  function validateForm() {
    let isValid = true;

    if (!titleInput.value.trim()) {
      titleInput.classList.add("is-invalid");
      titleInput.classList.remove("is-valid");
      isValid = false;
    } else {
      titleInput.classList.remove("is-invalid");
      titleInput.classList.add("is-valid");
    }

    if (!descriptionInput.value.trim()) {
      descriptionInput.classList.add("is-invalid");
      descriptionInput.classList.remove("is-valid");
      isValid = false;
    } else {
      descriptionInput.classList.remove("is-invalid");
      descriptionInput.classList.add("is-valid");
    }

    if (
      !githubLinkInput.dataset.verified ||
      githubLinkInput.dataset.verified === "false"
    ) {
      githubLinkInput.classList.add("is-invalid");
      githubLinkInput.classList.remove("is-valid");
      isValid = false;
    } else {
      githubLinkInput.classList.remove("is-invalid");
      githubLinkInput.classList.add("is-valid");
    }

    submitButton.disabled = !isValid;
    return isValid;
  }

  function clearGitHubData() {
    repoPreview.classList.remove("active", "loading", "error");
    repoName.textContent = "";
    repoStars.textContent = "";
    repoForks.textContent = "";
    repoUpdated.textContent = "";
    repoDescription.textContent = "";

    readmePreviewContainer.style.display = "none";
    readmePlaceholder.style.display = "flex";
    readmeMarkdown.style.display = "none";
    readmeLoading.style.display = "none";
    readmeMarkdown.innerHTML = "";

    githubLinkInput.dataset.verified = "false";

    if (titleInput.dataset.autoPopulated === "true") {
      titleInput.value = "";
      titleInput.classList.remove("is-valid");
      titleInput.dataset.autoPopulated = "false";
    }

    if (descriptionInput.dataset.autoPopulated === "true") {
      descriptionInput.value = "";
      descriptionInput.classList.remove("is-valid");
      charCount.textContent = "0";
      descriptionInput.dataset.autoPopulated = "false";
    }

    if (techStackInput.dataset.autoPopulated === "true") {
      techStackInput.value = "";
      updateTechPills();
      techStackInput.dataset.autoPopulated = "false";
    }
  }

  titleInput.addEventListener("input", function () {
    if (this.value.trim()) {
      this.classList.remove("is-invalid");
      this.classList.add("is-valid");
    } else {
      this.classList.add("is-invalid");
      this.classList.remove("is-valid");
    }
    validateForm();
  });

  descriptionInput.addEventListener("input", function () {
    if (this.value.trim()) {
      this.classList.remove("is-invalid");
      this.classList.add("is-valid");
    } else {
      this.classList.add("is-invalid");
      this.classList.remove("is-valid");
    }

    const count = this.value.length;
    charCount.textContent = count;

    if (count > MAX_CHARS * 0.9) {
      charCounter.classList.add("danger");
      charCounter.classList.remove("warning");
    } else if (count > MAX_CHARS * 0.7) {
      charCounter.classList.add("warning");
      charCounter.classList.remove("danger");
    } else {
      charCounter.classList.remove("warning", "danger");
    }

    validateForm();
  });

  githubLinkInput.addEventListener("input", function () {
    const githubRegex = /^https?:\/\/github\.com\/[\w-]+\/[\w.-]+\/?$/;

    clearGitHubData();

    if (this.value.trim() && githubRegex.test(this.value)) {
      fetchGitHubRepoInfo(this.value);
    } else {
      this.classList.add("is-invalid");
      this.classList.remove("is-valid");
      validateForm();
    }
  });

  function extractRepoInfo(url) {
    const match = url.match(/github\.com\/([^\/]+)\/([^\/]+)/);
    if (!match) return null;

    return {
      owner: match[1],
      repo: match[2].replace(/\/$/, ""),
    };
  }

  function fetchGitHubRepoInfo(url) {
    const repoInfo = extractRepoInfo(url);
    if (!repoInfo) {
      githubLinkInput.dataset.verified = "false";
      validateForm();
      return;
    }

    const { owner, repo } = repoInfo;

    repoPreview.classList.add("loading");
    repoPreview.classList.remove("error");
    githubLinkInput.dataset.verified = "false";
    validateForm();

    fetch(`https://api.github.com/repos/${owner}/${repo}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`GitHub API request failed: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        const updateDate = new Date(data.updated_at);
        const now = new Date();
        const diffTime = Math.abs(now - updateDate);
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

        let updatedText;
        if (diffDays === 0) {
          updatedText = "today";
        } else if (diffDays === 1) {
          updatedText = "yesterday";
        } else if (diffDays < 30) {
          updatedText = `${diffDays} days ago`;
        } else if (diffDays < 365) {
          const months = Math.floor(diffDays / 30);
          updatedText = `${months} month${months > 1 ? "s" : ""} ago`;
        } else {
          const years = Math.floor(diffDays / 365);
          updatedText = `${years} year${years > 1 ? "s" : ""} ago`;
        }

        repoName.textContent = data.name;
        repoStars.textContent = data.stargazers_count.toLocaleString();
        repoForks.textContent = data.forks_count.toLocaleString();
        repoUpdated.textContent = updatedText;
        repoDescription.textContent =
          data.description || "No description provided.";

        repoPreview.classList.remove("loading");
        repoPreview.classList.add("active");

        githubLinkInput.dataset.verified = "true";
        validateForm();

        if (!titleInput.value.trim()) {
          titleInput.value = data.name;
          titleInput.classList.add("is-valid");
          titleInput.dataset.autoPopulated = "true";
          validateForm();
        }

        if (!descriptionInput.value.trim() && data.description) {
          descriptionInput.value = data.description;
          descriptionInput.classList.add("is-valid");
          descriptionInput.dataset.autoPopulated = "true";
          charCount.textContent = data.description.length;
          validateForm();
        }

        fetchReadme(owner, repo);
        fetchRepoLanguages(owner, repo);
      })
      .catch((error) => {
        console.error("Error fetching GitHub repository data:", error);
        repoPreview.classList.remove("loading", "active");

        repoPreview.classList.add("error");
        repoDescription.textContent =
          "Repository not found or inaccessible. Please check the URL.";

        githubLinkInput.dataset.verified = "false";
        githubLinkInput.classList.add("is-invalid");
        githubLinkInput.classList.remove("is-valid");
        validateForm();

        readmePreviewContainer.style.display = "none";
        readmePlaceholder.style.display = "flex";
        readmeMarkdown.style.display = "none";
        readmeLoading.style.display = "none";
      });
  }

  function fetchReadme(owner, repo) {
    readmePreviewContainer.style.display = "flex";
    readmeLoading.style.display = "flex";
    readmePlaceholder.style.display = "none";
    readmeMarkdown.style.display = "none";

    fetch(`https://api.github.com/repos/${owner}/${repo}/readme`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`GitHub API request failed: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        const content = atob(data.content);
        readmeMarkdown.innerHTML = marked.parse(content);

        readmeLoading.style.display = "none";
        readmePlaceholder.style.display = "none";
        readmeMarkdown.style.display = "block";
      })
      .catch((error) => {
        console.error("Error fetching README:", error);
        readmeLoading.style.display = "none";

        readmePlaceholder.style.display = "flex";
        readmePlaceholder.innerHTML = `
          <i class="fas fa-exclamation-circle fa-3x text-warning mb-3"></i>
          <p>Could not find a README file in this repository</p>
        `;
        readmeMarkdown.style.display = "none";
      });
  }

  function fetchRepoLanguages(owner, repo) {
    fetch(`https://api.github.com/repos/${owner}/${repo}/languages`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`GitHub API request failed: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        const languages = Object.keys(data);

        if (languages.length > 0) {
          if (!techStackInput.value.trim()) {
            techStackInput.value = languages.join(", ");
            techStackInput.dataset.autoPopulated = "true";
            updateTechPills();
          }
        }
      })
      .catch((error) => {
        console.error("Error fetching languages:", error);
      });
  }

  function updateTechPills() {
    techPillsContainer.innerHTML = "";

    const techStack = techStackInput.value.trim();
    if (!techStack) return;

    const techs = techStack
      .split(",")
      .map((tech) => tech.trim())
      .filter((tech) => tech);

    techs.forEach((tech) => {
      if (tech) {
        const pill = document.createElement("div");
        pill.className = "tech-pill";

        const text = document.createElement("span");
        text.textContent = tech;

        const removeBtn = document.createElement("span");
        removeBtn.className = "remove-tech";
        removeBtn.innerHTML = "&times;";
        removeBtn.addEventListener("click", function () {
          const updatedTechs = techStackInput.value
            .split(",")
            .map((t) => t.trim())
            .filter((t) => t !== tech)
            .join(", ");

          techStackInput.value = updatedTechs;
          updateTechPills();
        });

        pill.appendChild(text);
        pill.appendChild(removeBtn);
        techPillsContainer.appendChild(pill);
      }
    });
  }

  techStackInput.addEventListener("blur", updateTechPills);
  techStackInput.addEventListener("keyup", function (e) {
    if (e.key === "," || e.key === "Enter") {
      updateTechPills();
    }
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    if (!validateForm()) {
      return false;
    }

    submitButton.classList.add("loading");
    submitButton.disabled = true;

    setTimeout(() => {
      this.submit();
    }, 2000);
  });

  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ["dragenter", "dragover"].forEach((eventName) => {
    dropArea.addEventListener(eventName, highlight, false);
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(eventName, unhighlight, false);
  });

  function highlight() {
    dropArea.classList.add("highlight");
  }

  function unhighlight() {
    dropArea.classList.remove("highlight");
  }

  dropArea.addEventListener("drop", handleDrop, false);

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length) {
      handleFiles(files);
    }
  }

  browseButton.addEventListener("click", function () {
    fileInput.click();
  });

  fileInput.addEventListener("change", function () {
    if (this.files.length) {
      handleFiles(this.files);
    }
  });

  removeButton.addEventListener("click", function () {
    preview.src = "";
    fileInput.value = "";
    dropArea.classList.remove("has-image");
  });

  function handleFiles(files) {
    const file = files[0];

    if (file.type.startsWith("image/")) {
      const reader = new FileReader();

      reader.onload = function (e) {
        preview.src = e.target.result;
        dropArea.classList.add("has-image");
      };

      reader.readAsDataURL(file);
    } else {
      alert("Please select an image file.");
    }
  }

  charCount.textContent = descriptionInput.value.length;

  if (techStackInput.value.trim()) {
    updateTechPills();
  }

  validateForm();

  if (githubLinkInput.value.trim()) {
    const githubRegex = /^https?:\/\/github\.com\/[\w-]+\/[\w.-]+\/?$/;
    if (githubRegex.test(githubLinkInput.value)) {
      fetchGitHubRepoInfo(githubLinkInput.value);
    }
  }

  // Use the hidden input for existing image rather than a visible image element
  const existingImageUrl = document.getElementById("existing-image-url");
  if (existingImageUrl && existingImageUrl.value) {
    preview.src = existingImageUrl.value;
    dropArea.classList.add("has-image");
  }
});
