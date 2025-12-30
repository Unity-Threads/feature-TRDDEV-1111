document.addEventListener('DOMContentLoaded', () => {

    /* -----------------------------------------------------
       🧭 0. Banner Carousels
    ----------------------------------------------------- */
    try {
        setupBannerCarousels();
    } catch (error) {
        console.error("Banner carousel error:", error);
    }

    /* -----------------------------------------------------
       🧭 1. Mobile Menu (Hamburger Toggle)
    ----------------------------------------------------- */
    try {
        const menuToggle = document.querySelector(".menu-toggle");
        const mobileMenu = document.querySelector(".mobile-menu");
        const closeMenuBtn = document.querySelector(".close-menu");

        if (menuToggle && mobileMenu) {
            menuToggle.addEventListener("click", (e) => {
                e.stopPropagation();
                mobileMenu.classList.add("active");
            });

            closeMenuBtn?.addEventListener("click", () => {
                mobileMenu.classList.remove("active");
            });

            mobileMenu.querySelectorAll("a").forEach(link => {
                link.addEventListener("click", () => {
                    mobileMenu.classList.remove("active");
                });
            });
        }

        document.addEventListener("click", (e) => {
            if (mobileMenu && !mobileMenu.contains(e.target) && e.target !== menuToggle) {
                mobileMenu.classList.remove("active");
            }
        });

        window.addEventListener("resize", () => {
            if (window.innerWidth > 768) {
                mobileMenu?.classList.remove("active");
            }
        });

    } catch (error) {
        console.error("Mobile menu error:", error);
    }

    /* -----------------------------------------------------
       👤 2. Profile Dropdown Menu (Desktop)
    ----------------------------------------------------- */
    try {
        const profileBtn = document.getElementById("profile-btn");
        const profileMenu = document.getElementById("profile-menu");

        if (profileBtn && profileMenu) {
            profileBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                profileMenu.classList.toggle("active");
            });

            document.addEventListener("click", (e) => {
                if (!profileMenu.contains(e.target) && e.target !== profileBtn) {
                    profileMenu.classList.remove("active");
                }
            });

            document.addEventListener("keydown", (e) => {
                if (e.key === "Escape") {
                    profileMenu.classList.remove("active");
                }
            });
        }
    } catch (error) {
        console.error("Profile dropdown error:", error);
    }

    /* -----------------------------------------------------
       💬 3. Login Popup Placeholder (for future use)
    ----------------------------------------------------- */


});
async function setupBannerCarousels() {
    try {
        // Fetch categories from Django API
        const response = await fetch("/api/categories/");
        const data = await response.json();
        const categories = data.categories;

        const sections = document.querySelectorAll('.banner-section');

        sections.forEach(section => {
            const categorySlug = section.dataset.category; // assuming you have data-category="electronics"
            const category = categories.find(cat => cat.slug === categorySlug);

            if (!category) {
                section.style.display = "none"; // hide if disabled or not found
                return;
            }

            const allImages = category.images || [];
            const shopLink = category.link || "#";

            const bannerLeft = section.querySelector('.banner-left');
            const bannerRight = section.querySelector('.banner-right');
            const dotsContainer = section.querySelector('.carousel-dots');
            const shopButton = section.querySelector('.shop-now-button');

            if (!bannerLeft || !bannerRight || !dotsContainer) return;

            shopButton.href = shopLink;

            let currentIndex = 0;
            let autoplayInterval;
            let dots = [];

            const isMobile = () => window.innerWidth <= 768;

            const renderDots = () => {
                dotsContainer.innerHTML = "";
                const dotCount = isMobile()
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
                        updateBanners();
                    });
                });
            };

            const updateBanners = () => {
                const setBanner = (banner, mediaUrl) => {
                    banner.innerHTML = "";
                    banner.style.backgroundImage = "none";
                    if (mediaUrl && (mediaUrl.endsWith(".mp4") || mediaUrl.endsWith(".webm"))) {
                        const video = document.createElement("video");
                        video.src = mediaUrl;
                        video.muted = true;
                        video.autoplay = true;
                        video.loop = true;
                        video.playsInline = true;
                        video.style.width = "100%";
                        video.style.height = "100%";
                        video.style.objectFit = "cover";
                        video.style.borderRadius = "10px";
                        banner.appendChild(video);
                    } else if (mediaUrl) {
                        banner.style.backgroundImage = `url('${mediaUrl}')`;
                    }
                };

                if (isMobile()) {
                    // Mobile: one image per slide
                    setBanner(bannerLeft, allImages[currentIndex]);
                    bannerRight.style.display = "none";
                } else {
                    // Desktop: two images per slide
                    const leftMedia = allImages[currentIndex * 2];
                    const rightMedia = allImages[currentIndex * 2 + 1];

                    if (rightMedia) {
                        // ✅ Normal case: 2 images
                        setBanner(bannerLeft, leftMedia);
                        bannerLeft.style.display = "block";
                        setBanner(bannerRight, rightMedia);
                        bannerRight.style.display = "block";
                        bannerLeft.style.width = "50%";
                        bannerRight.style.width = "50%";
                        bannerLeft.style.margin = "0";
                        bannerRight.style.margin = "0";
                    } else {
                        // ✅ Odd image count: only one image left
                        setBanner(bannerLeft, leftMedia);
                        bannerLeft.style.display = "block";
                        bannerRight.style.display = "none";

                        // Center the single image without stretching
                        bannerLeft.style.width = "50%";
                        bannerLeft.style.margin = "0 auto"; // centers it horizontally
                    }
                }



                dots.forEach(dot => dot.classList.remove("active"));
                if (dots[currentIndex]) dots[currentIndex].classList.add("active");
            };

            const nextBanner = () => {
                const maxIndex = isMobile()
                    ? allImages.length
                    : Math.ceil(allImages.length / 2);
                currentIndex = (currentIndex + 1) % maxIndex;
                updateBanners();
            };

            const startAutoplay = () => {
                autoplayInterval = setInterval(nextBanner, 2500);
            };

            renderDots();
            updateBanners();
            startAutoplay();

            window.addEventListener("resize", () => {
                currentIndex = 0;
                renderDots();
                updateBanners();
            });
        });

    } catch (error) {
        console.error("Error loading categories:", error);
    }
}


