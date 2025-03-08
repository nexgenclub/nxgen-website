document.addEventListener("DOMContentLoaded", function () {
  const githubLinkElement = document.getElementById("repo-github-link");

  if (!githubLinkElement) return;

  const githubLink = githubLinkElement.href;

  if (!githubLink || !githubLink.includes("github.com")) return;

  const urlParts = githubLink.replace("https://github.com/", "").split("/");
  const owner = urlParts[0];
  const repo = urlParts[1];

  if (!owner || !repo) {
    console.error(
      "Could not extract owner and repo from GitHub URL:",
      githubLink
    );
    return;
  }

  console.log("Fetching data for:", owner, repo);
  fetchRepoData(owner, repo);
  fetchReadmeContent(owner, repo);
});

function fetchRepoData(owner, repo) {
  fetch(`https://api.github.com/repos/${owner}/${repo}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error(
          `GitHub API request failed with status ${response.status}`
        );
      }
      return response.json();
    })
    .then((data) => {
      console.log("Repo data fetched:", data);
      updateProjectStats(data);
    })
    .catch((error) => {
      console.error("Error fetching GitHub data:", error);
    });
}

function updateProjectStats(repoData) {
  // Update star count
  const starCountElement = document.getElementById("star-count");
  if (starCountElement) {
    starCountElement.textContent = repoData.stargazers_count.toLocaleString();
  }

  // Update fork count
  const forkCountElement = document.getElementById("fork-count");
  if (forkCountElement) {
    forkCountElement.textContent = repoData.forks_count.toLocaleString();
  }

  // Update watcher count
  const watchCountElement = document.getElementById("watch-count");
  if (watchCountElement) {
    watchCountElement.textContent = repoData.subscribers_count.toLocaleString();
  }

  // Update issue count
  const issueCountElement = document.getElementById("issue-count");
  if (issueCountElement) {
    issueCountElement.textContent = repoData.open_issues_count.toLocaleString();
  }

  // Update description if available
  const descriptionElement = document.getElementById("project-description");
  if (descriptionElement && repoData.description) {
    descriptionElement.textContent = repoData.description;
  }

  // Fetch languages for tech stack
  fetchLanguages(repoData.owner.login, repoData.name);
}

function fetchLanguages(owner, repo) {
  fetch(`https://api.github.com/repos/${owner}/${repo}/languages`)
    .then((response) => {
      if (!response.ok) {
        throw new Error(
          `GitHub API languages request failed with status ${response.status}`
        );
      }
      return response.json();
    })
    .then((languages) => {
      console.log("Languages fetched:", languages);
      const techStackElement = document.getElementById("tech-stack-container");
      if (techStackElement && Object.keys(languages).length > 0) {
        techStackElement.innerHTML = "";

        Object.keys(languages).forEach((language) => {
          const badge = document.createElement("span");
          badge.className = "badge bg-light text-dark border";
          badge.textContent = language;
          techStackElement.appendChild(badge);
        });
      }
    })
    .catch((error) => {
      console.error("Error fetching languages:", error);
    });
}

function fetchReadmeContent(owner, repo) {
  fetch(`https://api.github.com/repos/${owner}/${repo}/readme`)
    .then((response) => {
      if (!response.ok) {
        throw new Error(
          `GitHub API README request failed with status ${response.status}`
        );
      }
      return response.json();
    })
    .then((data) => {
      console.log("README data fetched");
      // Decode the Base64 content
      const decodedContent = atob(data.content);

      // Convert markdown to HTML
      const readmeHTML = convertMarkdownToHTML(decodedContent);

      // Update the README section
      const readmeContentElement = document.querySelector(".readme-content");
      if (readmeContentElement) {
        readmeContentElement.innerHTML = readmeHTML;

        // Apply syntax highlighting if available
        applySyntaxHighlighting();
      }
    })
    .catch((error) => {
      console.error("Error fetching README:", error);
      const readmeContentElement = document.querySelector(".readme-content");
      if (readmeContentElement) {
        readmeContentElement.innerHTML =
          '<div class="alert alert-warning">Unable to load README from GitHub. Please check the repository link.</div>';
      }
    });
}

function convertMarkdownToHTML(markdown) {
  let html = markdown
    .replace(/^### (.*$)/gm, "<h3>$1</h3>")
    .replace(/^## (.*$)/gm, "<h2>$1</h2>")
    .replace(/^# (.*$)/gm, "<h1>$1</h1>")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/```([^`]+)```/g, "<pre><code>$1</code></pre>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
    .replace(/^\s*\-\s(.*$)/gm, "<li>$1</li>")
    .replace(/^\s*(\n)?([^\n]+)/gm, function (m) {
      return /^\s*\<(\/)?(h\d|ul|ol|li|blockquote|pre|img)/.test(m)
        ? m
        : "<p>" + m + "</p>";
    });

  html = html.replace(/<li>.*?<\/li>/gs, function (m) {
    return "<ul>" + m + "</ul>";
  });

  return html;
}

function applySyntaxHighlighting() {
  const codeBlocks = document.querySelectorAll("pre code");
  if (codeBlocks.length > 0) {
    if (!document.querySelector('script[src*="highlight.js"]')) {
      const highlightCSS = document.createElement("link");
      highlightCSS.rel = "stylesheet";
      highlightCSS.href =
        "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github.min.css";
      document.head.appendChild(highlightCSS);

      const highlightJS = document.createElement("script");
      highlightJS.src =
        "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js";
      highlightJS.onload = function () {
        hljs.highlightAll();
      };
      document.body.appendChild(highlightJS);
    } else if (typeof hljs !== "undefined") {
      hljs.highlightAll();
    }
  }
}
