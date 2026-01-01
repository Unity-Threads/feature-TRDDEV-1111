
// Run script after page is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    setupBannerCarousel();
    setupProfileDropdown();
    setupMobileMenu();
    setupLoginForgotModals();
    setupMobileProfileDropdown();
    setupNewsletterForm();
    setupToastAutoRemove();
});

function setupBannerCarousel() {
    // Images for the carousel
    const allImages = [
        'https://placehold.co/500x400/C8C8C8/424242?text=New+Collection',
        'https://placehold.co/500x400/D3D3D3/424242?text=Spring+Looks',
        'https://placehold.co/500x400/B0C4DE/424242?text=Urban+Wear',
        'https://placehold.co/500x400/ADD8E6/424242?text=Cool+Vibes',
        'https://placehold.co/500x400/F5DEB3/424242?text=Summer+Sale',
        'https://placehold.co/500x400/FFDAB9/424242?text=Accessories'
    ];

    // DOM elements
    const bannerLeft = document.getElementById('banner-left');
    const bannerRight = document.getElementById('banner-right');
    const dotsContainer = document.querySelector('.carousel-dots');

    if (!bannerLeft || !bannerRight || !dotsContainer) {
        return; // Exit if no carousel on this page
    }

    let dots = [];
    let currentIndex = 0;
    let autoplayInterval;

    const isMobile = () => window.innerWidth <= 768;

    const renderDots = () => {
        dotsContainer.innerHTML = "";
        let dotCount = isMobile()
            ? allImages.length
            : Math.ceil(allImages.length / 2);
        for (let i = 0; i < dotCount; i++) {
            const dot = document.createElement("span");
            dot.classList.add("dot");
            if (i === currentIndex) dot.classList.add("active");
            dot.dataset.index = i;
            dotsContainer.appendChild(dot);
        }
        dots = Array.from(dotsContainer.querySelectorAll(".dot"));
        dots.forEach(dot => {
            dot.addEventListener("click", (e) => {
                currentIndex = parseInt(e.target.dataset.index);
                updateBanners(currentIndex);
                stopAutoplay();
                startAutoplay();
            });
        });
    };

    const updateBanners = (index) => {
        const clearBanner = (banner) => {
            banner.innerHTML = "";
            banner.style.backgroundImage = "none";
        };
        const setBanner = (banner, mediaUrl) => {
            clearBanner(banner);
            if (mediaUrl.endsWith(".mp4") || mediaUrl.endsWith(".webm")) {
                const video = document.createElement("video");
                video.src = mediaUrl;
                video.controls = true;
                video.preload = "metadata";
                video.playsInline = true;
                video.style.width = "100%";
                video.style.height = "100%";
                video.style.objectFit = "cover";
                video.style.borderRadius = "10px";
                banner.appendChild(video);
                video.addEventListener("play", stopAutoplay);
                video.addEventListener("ended", startAutoplay);
                video.addEventListener("pause", () => {
                    if (video.currentTime < video.duration) {
                        startAutoplay();
                    }
                });
            } else {
                banner.style.backgroundImage = `url('${mediaUrl}')`;
            }
        };
        if (isMobile()) {
            setBanner(bannerLeft, allImages[index]);
            bannerRight.style.display = "none";
        } else {
            const leftMedia = allImages[index * 2];
            const rightMedia = allImages[index * 2 + 1];
            setBanner(bannerLeft, leftMedia);
            bannerLeft.style.display = "block";
            if (rightMedia) {
                setBanner(bannerRight, rightMedia);
                bannerRight.style.display = "block";
            } else {
                bannerRight.style.display = "none";
            }
        }
        dots.forEach(dot => dot.classList.remove("active"));
        if (dots[index]) dots[index].classList.add("active");
    };

    const nextBanner = () => {
        let maxIndex = isMobile()
            ? allImages.length
            : Math.ceil(allImages.length / 2);
        currentIndex = (currentIndex + 1) % maxIndex;
        updateBanners(currentIndex);
    };

    const prevBanner = () => {
        let maxIndex = isMobile()
            ? allImages.length
            : Math.ceil(allImages.length / 2);
        currentIndex = (currentIndex - 1 + maxIndex) % maxIndex;
        updateBanners(currentIndex);
    };

    const startAutoplay = () => {
        autoplayInterval = setInterval(nextBanner, 2500);
    };
    const stopAutoplay = () => {
        clearInterval(autoplayInterval);
        autoplayInterval = null;
    };

    renderDots();
    updateBanners(currentIndex);
    startAutoplay();

    [bannerLeft, bannerRight].forEach(banner => {
        banner.addEventListener('mouseenter', stopAutoplay);
        banner.addEventListener('mouseleave', startAutoplay);
    });

    window.addEventListener("resize", () => {
        currentIndex = 0;
        renderDots();
        updateBanners(currentIndex);
    });

    let startX = 0;
    let endX = 0;
    const touchElements = [bannerLeft, bannerRight];
    touchElements.forEach(element => {
        element.addEventListener("touchstart", (e) => {
            startX = e.touches[0].clientX;
        });
        element.addEventListener("touchmove", (e) => {
            e.preventDefault();
        });
        element.addEventListener("touchend", (e) => {
            endX = e.changedTouches[0].clientX;
            handleSwipe();
        });
    });
    const handleSwipe = () => {
        const diff = startX - endX;
        if (Math.abs(diff) > 50) {
            if (diff > 0) {
                nextBanner();
            } else {
                prevBanner();
            }
            stopAutoplay();
            startAutoplay();
        }
        startX = 0;
        endX = 0;
    };
}

function setupProfileDropdown() {
    const profileBtn = document.getElementById("profile-btn");
    const profileMenu = document.getElementById("profile-menu");
    if (profileBtn && profileMenu) {
        profileBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            profileMenu.classList.toggle("active");
        });
        document.addEventListener("click", (e) => {
            if (!profileMenu.contains(e.target) && !profileBtn.contains(e.target)) {
                profileMenu.classList.remove("active");
            }
        });
    }
}

function setupMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    const closeMenuBtn = document.querySelector('.close-menu');
    if (menuToggle && mobileMenu && closeMenuBtn) {
        menuToggle.addEventListener('click', () => {
            mobileMenu.classList.add('active');
        });
        closeMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.remove('active');
        });
        mobileMenu.addEventListener('click', (e) => {
            if (e.target === mobileMenu) {
                mobileMenu.classList.remove('active');
            }
        });
    }
}

function setupLoginForgotModals() {
    const loginBtns = document.querySelectorAll(".login");
    loginBtns.forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            window.location.href = "/login/";
        });
    });
}

function setupMobileProfileDropdown() {
    const mobileProfileBtn = document.querySelector(".mobile-profile-btn");
    const mobileDropdownMenu = document.querySelector(".mobile-dropdown-menu");
    if (mobileProfileBtn && mobileDropdownMenu) {
        mobileProfileBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            mobileDropdownMenu.classList.toggle("active");
        });
        document.addEventListener("click", (e) => {
            if (!mobileDropdownMenu.contains(e.target) && !mobileProfileBtn.contains(e.target)) {
                mobileDropdownMenu.classList.remove("active");
            }
        });
    }
}

function setupNewsletterForm() {
    const form = document.querySelector(".newsletter");
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });
            if (response.ok) {
                alert("Thank you for subscribing!");
                form.reset();
            } else {
                alert("Something went wrong. Try again.");
            }
        });
    }
}

function setupToastAutoRemove() {
    const toasts = document.querySelectorAll(".toast");
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.remove();
        }, 5000);
    });
}