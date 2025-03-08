document.addEventListener("DOMContentLoaded", function () {
  // Elements for image upload
  const dropArea = document.getElementById("drop-area");
  const fileInput = document.getElementById("fileElem");
  const preview = document.getElementById("preview");
  const browseButton = document.getElementById("browseButton");
  const removeButton = document.querySelector(".remove-image");

  // Form elements for validation
  const form = document.getElementById("projectForm");
  const titleInput = document.querySelector("input[name='title']");
  const descriptionInput = document.querySelector(
    "textarea[name='description']"
  );
  const githubLinkInput = document.querySelector("input[name='github_link']");
  const techStackInput = document.querySelector("input[name='tech_stack']");
  const submitButton = document.getElementById("submitButton");

  // Character counter for description
  const charCounter = document.querySelector(".char-counter");
  const charCount = document.getElementById("char-count");
  const charMax = document.getElementById("char-max");
  const MAX_CHARS = 500;
  charMax.textContent = MAX_CHARS;

  // Tech stack pills container
  const techPillsContainer = document.getElementById("tech-pills-container");

  // GitHub repository preview
  const repoPreview = document.getElementById("repo-preview");
  const repoName = document.getElementById("repo-name");
  const repoStars = document.getElementById("repo-stars");
  const repoForks = document.getElementById("repo-forks");
  const repoUpdated = document.getElementById("repo-updated");
  const repoDescription = document.getElementById("repo-description");

  // README preview elements
  const readmePreviewContainer = document.querySelector(
    ".readme-preview-container"
  );
  const readmeContent = document.getElementById("readme-content");
  const readmePlaceholder = document.getElementById("readme-placeholder");
  const readmeMarkdown = document.getElementById("readme-markdown");
  const readmeLoading = document.getElementById("readme-loading");

  // Add CSS for error state
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

  // Hide README container initially
  readmePreviewContainer.style.display = "none";

  // Set submit button as initially disabled
  submitButton.disabled = true;

  // Form validation
  function validateForm() {
    let isValid = true;

    // Validate title
    if (!titleInput.value.trim()) {
      titleInput.classList.add("is-invalid");
      titleInput.classList.remove("is-valid");
      isValid = false;
    } else {
      titleInput.classList.remove("is-invalid");
      titleInput.classList.add("is-valid");
    }

    // Validate description
    if (!descriptionInput.value.trim()) {
      descriptionInput.classList.add("is-invalid");
      descriptionInput.classList.remove("is-valid");
      isValid = false;
    } else {
      descriptionInput.classList.remove("is-invalid");
      descriptionInput.classList.add("is-valid");
    }

    // Validate GitHub link - the link must be verified by the API to be valid
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

    // Update submit button state
    submitButton.disabled = !isValid;

    return isValid;
  }

  // Live input validation
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

    // Update character counter
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
    if (this.value.trim() && githubRegex.test(this.value)) {
      fetchGitHubRepoInfo(this.value);
    } else {
      this.classList.add("is-invalid");
      this.classList.remove("is-valid");
      this.dataset.verified = "false";
      validateForm();
      repoPreview.classList.remove("active");

      // Hide README preview container
      readmePreviewContainer.style.display = "none";
      readmePlaceholder.style.display = "flex";
      readmeMarkdown.style.display = "none";
      readmeLoading.style.display = "none";
    }
  });

  // Extract owner and repo from GitHub URL
  function extractRepoInfo(url) {
    const match = url.match(/github\.com\/([^\/]+)\/([^\/]+)/);
    if (!match) return null;

    return {
      owner: match[1],
      repo: match[2].replace(/\/$/, ""), // Remove trailing slash if present
    };
  }

  // GitHub repository info fetch
  function fetchGitHubRepoInfo(url) {
    const repoInfo = extractRepoInfo(url);
    if (!repoInfo) {
      githubLinkInput.dataset.verified = "false";
      validateForm();
      return;
    }

    const { owner, repo } = repoInfo;

    // Show loading state
    repoPreview.classList.add("loading");
    repoPreview.classList.remove("error");
    githubLinkInput.dataset.verified = "false";
    validateForm();

    // Fetch data from GitHub API
    fetch(`https://api.github.com/repos/${owner}/${repo}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`GitHub API request failed: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        // Format the date
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

        // Update the repository preview
        repoName.textContent = data.name;
        repoStars.textContent = data.stargazers_count.toLocaleString();
        repoForks.textContent = data.forks_count.toLocaleString();
        repoUpdated.textContent = updatedText;
        repoDescription.textContent =
          data.description || "No description provided.";

        // Remove loading state and show the preview
        repoPreview.classList.remove("loading");
        repoPreview.classList.add("active");

        // Mark GitHub link as verified
        githubLinkInput.dataset.verified = "true";
        validateForm();

        // Auto-fill project title if empty
        if (!titleInput.value.trim()) {
          titleInput.value = data.name;
          titleInput.classList.add("is-valid");
          validateForm();
        }

        // Auto-fill project description if empty
        if (!descriptionInput.value.trim() && data.description) {
          descriptionInput.value = data.description;
          descriptionInput.classList.add("is-valid");
          charCount.textContent = data.description.length;
          validateForm();
        }

        // Fetch README
        fetchReadme(owner, repo);

        // Fetch repository languages for tech stack
        fetchRepoLanguages(owner, repo);
      })
      .catch((error) => {
        console.error("Error fetching GitHub repository data:", error);
        repoPreview.classList.remove("loading", "active");

        // Show error message in the UI
        repoPreview.classList.add("error");
        repoDescription.textContent =
          "Repository not found or inaccessible. Please check the URL.";

        // Mark GitHub link as not verified
        githubLinkInput.dataset.verified = "false";
        githubLinkInput.classList.add("is-invalid");
        githubLinkInput.classList.remove("is-valid");
        validateForm();

        // Hide README preview container
        readmePreviewContainer.style.display = "none";
        readmePlaceholder.style.display = "flex";
        readmeMarkdown.style.display = "none";
        readmeLoading.style.display = "none";
      });
  }

  // Fetch and display README from GitHub
  function fetchReadme(owner, repo) {
    // Show README preview container
    readmePreviewContainer.style.display = "flex";

    // Show loading state
    readmeLoading.style.display = "flex";
    readmePlaceholder.style.display = "none";
    readmeMarkdown.style.display = "none";

    // Fetch README content from GitHub API
    fetch(`https://api.github.com/repos/${owner}/${repo}/readme`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`GitHub API request failed: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        // Decode the Base64 content
        const content = atob(data.content);

        // Convert Markdown to HTML using marked library
        readmeMarkdown.innerHTML = marked.parse(content);

        // Show the README content
        readmeLoading.style.display = "none";
        readmePlaceholder.style.display = "none";
        readmeMarkdown.style.display = "block";
      })
      .catch((error) => {
        console.error("Error fetching README:", error);
        readmeLoading.style.display = "none";

        // Show placeholder with error message
        readmePlaceholder.style.display = "flex";
        readmePlaceholder.innerHTML = `
          <i class="fas fa-exclamation-circle fa-3x text-warning mb-3"></i>
          <p>Could not find a README file in this repository</p>
        `;
        readmeMarkdown.style.display = "none";
      });
  }

  // Fetch repository languages for tech stack
  function fetchRepoLanguages(owner, repo) {
    fetch(`https://api.github.com/repos/${owner}/${repo}/languages`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`GitHub API request failed: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        // Extract languages from response
        const languages = Object.keys(data);

        if (languages.length > 0) {
          // Add languages to tech stack input if it's empty
          if (!techStackInput.value.trim()) {
            techStackInput.value = languages.join(", ");
            updateTechPills();
          }
        }
      })
      .catch((error) => {
        console.error("Error fetching languages:", error);
      });
  }

  // Tech stack pills
  function updateTechPills() {
    // Clear existing pills
    techPillsContainer.innerHTML = "";

    // Get tech stack value and split by commas
    const techStack = techStackInput.value.trim();
    if (!techStack) return;

    const techs = techStack
      .split(",")
      .map((tech) => tech.trim())
      .filter((tech) => tech);

    // Create pills for each tech
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
          // Remove this tech from the input value
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

  // Form submission with loading state
  form.addEventListener("submit", function (e) {
    e.preventDefault();

    // Validate form first
    if (!validateForm()) {
      return false;
    }

    // Set loading state
    submitButton.classList.add("loading");
    submitButton.disabled = true;

    // Simulate form submission (remove in real implementation)
    setTimeout(() => {
      // In a real implementation, you would submit the form here
      this.submit();
    }, 2000);
  });

  // Prevent default drag behaviors for image upload
  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  // Highlight drop area when item is dragged over it
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

  // Handle dropped files
  dropArea.addEventListener("drop", handleDrop, false);

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length) {
      handleFiles(files);
    }
  }

  // Browse button click handler
  browseButton.addEventListener("click", function () {
    fileInput.click();
  });

  // File input change handler
  fileInput.addEventListener("change", function () {
    if (this.files.length) {
      handleFiles(this.files);
    }
  });

  // Remove image button click handler
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

  // Initialize character count
  charCount.textContent = descriptionInput.value.length;

  // Initialize tech pills if there's initial value
  if (techStackInput.value.trim()) {
    updateTechPills();
  }

  // Run initial validation
  validateForm();

  // Initialize GitHub repo preview if there's a valid URL
  if (githubLinkInput.value.trim()) {
    const githubRegex = /^https?:\/\/github\.com\/[\w-]+\/[\w.-]+\/?$/;
    if (githubRegex.test(githubLinkInput.value)) {
      fetchGitHubRepoInfo(githubLinkInput.value);
    }
  }
});
