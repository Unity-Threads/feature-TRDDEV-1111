document.addEventListener("DOMContentLoaded", () => {
  // === Elements ===
  const editBtns = document.querySelectorAll(".edit-btn");
  const saveBtn = document.getElementById("save-btn");
  const discardBtns = document.querySelectorAll(".discard-btn");
  const changePasswordBtn = document.getElementById("changePassBtn");
  const nameInput = document.getElementById("name");
  const emailInput = document.getElementById("email");
  const errorEl = document.getElementById("profile-error");
  const successEl = document.getElementById("profile-success");

  const modal = document.getElementById("passwordModal");
  const passwordBtns = document.querySelectorAll(".password-btn");
  const closeModal = document.querySelector(".close");
  const passwordForm = document.getElementById("passwordForm");

  // Store initial values for discard
  let initialName = nameInput ? nameInput.value : "";
  let initialEmail = emailInput ? emailInput.value : "";

  /* ===========================
        HELPER FUNCTIONS
  =========================== */

  function switchToEditMode() {
    if (!nameInput || !emailInput) return;

    nameInput.disabled = false;
    emailInput.disabled = false;

    nameInput.focus();

    // Focus styles
    nameInput.style.border = "1px solid #a6b3f2";
    nameInput.style.boxShadow = "0 0 10px #a6b3f2";
    nameInput.style.backgroundColor = "#ffffff";

    emailInput.style.border = "1px solid #a6b3f2";
    emailInput.style.boxShadow = "0 0 10px #a6b3f2";
    emailInput.style.backgroundColor = "#ffffff";

    // Show save + discard using inline style
    if (saveBtn) saveBtn.style.display = "inline-block";
    discardBtns.forEach(btn => {
      btn.style.display = "inline-block";
    });

    // Hide all edit buttons (desktop + mobile)
    editBtns.forEach(btn => {
      btn.style.display = "none";
    });

    errorEl.textContent = "";
    successEl.textContent = "";
  }

  function resetFormUI() {
    if (!nameInput || !emailInput) return;

    nameInput.disabled = true;
    emailInput.disabled = true;

    // Reset to normal styles
    nameInput.style.border = "1px solid var(--border)";
    nameInput.style.boxShadow = "none";
    nameInput.style.backgroundColor = "#f9fafb";

    emailInput.style.border = "1px solid var(--border)";
    emailInput.style.boxShadow = "none";
    emailInput.style.backgroundColor = "#f9fafb";

    // Hide save + discard via inline style
    if (saveBtn) saveBtn.style.display = "none";
    discardBtns.forEach(btn => {
      // Clear inline style so CSS (desktop/mobile) can decide
      btn.style.display = "";
    });

    // IMPORTANT: clear inline display so your CSS desktop/mobile
    // rules decide which edit button is visible.
    editBtns.forEach(btn => {
      btn.style.display = "";
    });
  }

  /* ===========================
        EDIT BUTTONS
  =========================== */

  editBtns.forEach(btn => {
    btn.addEventListener("click", switchToEditMode);
  });

  /* ===========================
        DISCARD BUTTONS
  =========================== */

  discardBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      // Reset values
      nameInput.value = initialName;
      emailInput.value = initialEmail;

      resetFormUI();
      errorEl.textContent = "";
      successEl.textContent = "";
    });
  });

  /* ===========================
        SAVE PROFILE (AJAX)
  =========================== */

  if (saveBtn) {
    saveBtn.addEventListener("click", async () => {
      errorEl.textContent = "";
      successEl.textContent = "";

      const formData = new FormData();
      formData.append("name", nameInput.value);
      formData.append("email", emailInput.value);
      formData.append(
        "csrfmiddlewaretoken",
        document.querySelector("[name=csrfmiddlewaretoken]").value
      );

      try {
        const response = await fetch("/profile/ajax/save-profile/", {
          method: "POST",
          body: formData,
        });

        const data = await response.json();

        if (data.success) {
          successEl.textContent = data.message || "Profile updated successfully.";
          initialName = nameInput.value;
          initialEmail = emailInput.value;
          // Lock fields again
          resetFormUI();

          // Update username in mobile view
          const mobileViewUserName = document.querySelector("#mobile_username");
          if (mobileViewUserName) {
            mobileViewUserName.textContent = "Hello " + nameInput.value;
          }

          // Update username in header profile menu
          const headerUserName = document.querySelector(".profile-menu .user-name");
          if (headerUserName) {
            headerUserName.textContent = "Hello " + nameInput.value;
          }
          // Optional: if server returns canonical name/email, prefer that
          if (data.name) {
            nameInput.value = data.name;
            initialName = data.name;
          }
          if (data.email) {
            emailInput.value = data.email;
            initialEmail = data.email;
          }
        } else {
          errorEl.textContent = data.error || "Enter valid email";
        }
      } catch {
        errorEl.textContent = "Error updating profile. Try again.";
      }
    });
  }

  /* ===========================
        PASSWORD MODAL
  =========================== */

  passwordBtns.forEach(btn =>
    btn.addEventListener("click", () => {
      modal.style.display = "block";
    })
  );

  closeModal.addEventListener("click", () => {
    modal.style.display = "none";
  });

  window.addEventListener("click", e => {
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });

  /* ===========================
        PASSWORD STRENGTH
  =========================== */

  const newPassInput = document.getElementById("new_password1");
  const strengthBar = document.getElementById("password-strength-bar");
  const strengthText = document.getElementById("strength-text");

  if (newPassInput && strengthBar && strengthText) {
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

  /* ===========================
        CHANGE PASSWORD (AJAX)
  =========================== */

  if (!passwordForm || !changePasswordBtn) return;

  passwordForm.addEventListener("submit", async e => {
    e.preventDefault();

    const pwdErrorEl = document.getElementById("password-error");
    const pwdSuccessEl = document.getElementById("password-success");
    pwdErrorEl.textContent = "";
    pwdSuccessEl.textContent = "";

    changePasswordBtn.disabled = true;
    changePasswordBtn.textContent = "Changing Password...";
    changePasswordBtn.classList.add("loading");

    await new Promise(requestAnimationFrame);

    try {
      const response = await fetch("/profile/ajax/change-password/", {
        method: "POST",
        body: new URLSearchParams(new FormData(passwordForm)),
        headers: {
          "X-CSRFToken": document.querySelector(
            "[name=csrfmiddlewaretoken]"
          ).value,
        },
        credentials: "same-origin",
      });

      const data = await response.json();

      if (data.success) {
        pwdSuccessEl.textContent = data.message;
        passwordForm.reset();
      } else {
        pwdErrorEl.textContent = data.error;
      }
    } catch {
      pwdErrorEl.textContent = "Something went wrong.";
    } finally {
      changePasswordBtn.disabled = false;
      changePasswordBtn.textContent = "Change Password";
      changePasswordBtn.classList.remove("loading");

    }
  });

  /* ===========================
        AUTO CLEAR SUCCESS MSGS
  =========================== */

  function autoClearMessage(id, timeout) {
    const el = document.getElementById(id);
    if (!el) return;

    const observer = new MutationObserver(() => {
      if (el.textContent.trim() !== "") {
        setTimeout(() => {
          el.textContent = "";
        }, timeout);
      }
    });

    observer.observe(el, {
      childList: true,
      characterData: true,
      subtree: true,
    });
  }

  autoClearMessage("profile-success", 4000);
  autoClearMessage("password-success", 4000);
});
