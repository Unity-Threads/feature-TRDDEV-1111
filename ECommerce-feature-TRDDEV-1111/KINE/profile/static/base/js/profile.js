document.addEventListener("DOMContentLoaded", () => {
  // === Elements ===
  const editBtn = document.getElementById("edit-btn");
  const saveBtn = document.getElementById("save-btn");
  const nameInput = document.getElementById("name");
  const emailInput = document.getElementById("email");
  const errorEl = document.getElementById("profile-error");
  const successEl = document.getElementById("profile-success");

  const avatarInput = document.getElementById("avatar-input");
  const avatarImg = document.getElementById("avatar-img");

  const modal = document.getElementById("passwordModal");
  const passwordBtn = document.getElementById("password-btn");
  const closeModal = document.querySelector(".close");
  const passwordForm = document.getElementById("passwordForm");

  // === Edit / Save Profile ===
  editBtn.addEventListener("click", () => {
    nameInput.disabled = false;
    emailInput.disabled = false;
    saveBtn.style.display = "inline-block";
    editBtn.style.display = "none";
    errorEl.textContent = "";
    successEl.textContent = "";
  });

  saveBtn.addEventListener("click", async () => {
    errorEl.textContent = "";
    successEl.textContent = "";

    const formData = new FormData();
    formData.append("name", nameInput.value);
    formData.append("email", emailInput.value);
    formData.append("csrfmiddlewaretoken", document.querySelector("[name=csrfmiddlewaretoken]").value);

    try {
      const response = await fetch("/ajax/save-profile/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        successEl.textContent = data.message || "Profile updated successfully.";
        nameInput.disabled = true;
        emailInput.disabled = true;
        saveBtn.style.display = "none";
        editBtn.style.display = "inline-block";
      } else {
        errorEl.textContent = data.error || "Enter valid email";
      }
    } catch {
      errorEl.textContent = "Error updating profile. Try again.";
    }
  });

  // === Avatar Upload ===
  avatarInput.addEventListener("change", async () => {
    const formData = new FormData();
    formData.append("avatar", avatarInput.files[0]);
    formData.append("csrfmiddlewaretoken", document.querySelector("[name=csrfmiddlewaretoken]").value);

    const response = await fetch("/ajax/upload-avatar/", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (data.success) avatarImg.src = data.avatar_url;
  });

  // === Password Modal Handling ===
  passwordBtn.addEventListener("click", () => (modal.style.display = "block"));
  closeModal.addEventListener("click", () => (modal.style.display = "none"));
  window.onclick = e => { if (e.target === modal) modal.style.display = "none"; };

  // === Password Strength Indicator ===
  const newPassInput = document.getElementById("new_password1");
  const strengthBar = document.getElementById("password-strength-bar");
  const strengthText = document.getElementById("strength-text");

  if (newPassInput) {
    newPassInput.addEventListener("input", () => {
      const val = newPassInput.value;
      let strength = 0;
      if (val.length >= 8) strength++;
      if (/[A-Z]/.test(val)) strength++;
      if (/[a-z]/.test(val)) strength++;
      if (/\d/.test(val)) strength++;
      if (/[!@#$%^&*(),.?":{}|<>]/.test(val)) strength++;

      const percent = (strength / 5) * 100;
      strengthBar.style.width = percent + "%";

      if (percent < 40) {
        strengthBar.style.background = "linear-gradient(90deg, red, orange)";
        strengthText.textContent = "Weak";
        strengthText.style.color = "red";
      } else if (percent < 70) {
        strengthBar.style.background = "linear-gradient(90deg, orange, yellow)";
        strengthText.textContent = "Fair";
        strengthText.style.color = "orange";
      } else if (percent < 90) {
        strengthBar.style.background = "linear-gradient(90deg, yellow, #00b300)";
        strengthText.textContent = "Good";
        strengthText.style.color = "#b3a000";
      } else {
        strengthBar.style.background = "linear-gradient(90deg, #00b300, #00e600)";
        strengthText.textContent = "Strong";
        strengthText.style.color = "green";
      }
    });
  }

  // === Change Password (AJAX) ===
  passwordForm.addEventListener("submit", async e => {
    e.preventDefault();
    const errorEl = document.getElementById("password-error");
    const successEl = document.getElementById("password-success");
    errorEl.textContent = "";
    successEl.textContent = "";

    const response = await fetch("/ajax/change-password/", {
      method: "POST",
      body: new URLSearchParams(new FormData(passwordForm)),
      headers: { "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value },
    });

    const data = await response.json();
    if (data.success) {
      successEl.textContent = data.message || "Password changed successfully!";
      passwordForm.reset();
      strengthBar.style.width = "0%";
      strengthText.textContent = "";
      setTimeout(() => (modal.style.display = "none"), 1500);
    } else {
      errorEl.textContent =
        data.error || "Password must be 8+ chars with uppercase, lowercase, number & special character";
    }
  });

  // === Show/Hide Password Toggle (Now Inside DOMContentLoaded) ===
  document.querySelectorAll(".toggle-password").forEach(icon => {
    icon.addEventListener("click", function () {
      const inputId = this.getAttribute("data-target");
      const input = document.getElementById(inputId);
      if (!input) return;

      if (input.type === "password") {
        input.type = "text";
        this.classList.add("active");
        this.classList.remove("fa-eye");
        this.classList.add("fa-eye-slash");
        this.setAttribute("title", "Hide Password");
      } else {
        input.type = "password";
        this.classList.remove("active");
        this.classList.remove("fa-eye-slash");
        this.classList.add("fa-eye");
        this.setAttribute("title", "Show Password");
      }
    });
  });
});
