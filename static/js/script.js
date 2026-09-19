// dark light mode
const themeToggle=document.getElementById("themeToggle");
themeToggle.addEventListener("click",function(){
    document.body.classList.toggle("dark-mode");
    const icon=themeToggle.querySelector("i");
    if(document.body.classList.contains("dark-mode")){
        icon.classList.remove("fa-moon");
        icon.classList.add("fa-sun");
    }else{
        icon.classList.remove("fa-sun");
        icon.classList.add("fa-moon");
    }
});

// destination search

const destinationSearch=document.getElementById("destinationSearch");
const travelDate=document.getElementById("travelDate");
const searchBtn=document.getElementById("searchBtn");

// searchBtn.addEventListener("click",function(){
//     const destination=destinationSearch.value.trim();
//     if(destination==""){
//         alert("please enter a destination!");
//         return;
//     }
//     alert("Searching for:"+destination);
// });
// search destinaction card
searchBtn.addEventListener("click",function(){
    const searchValue=destinationSearch.value.trim().toLowerCase();
    if(searchValue===""){
        alert("please enter a destination");
        return;
    }
    const destinationCards=document.querySelectorAll(".destination-card");
    let found =false;
    destinationCards.forEach(function(card){
        const destinationName=card.querySelector("h3").textContent.toLowerCase();
        if(destinationName.includes(searchValue)){
            found=true;
            card.scrollIntoView({
                behavior:"smooth",
                block:"center"
            });
            card.style.outline="4px solid #facc15";
            setTimeout(function(){
                card.style.outline="none";
            },3000);
        }
    });
    if(!found){
        alert("Destinaction not found");
    }
});
// wishlist
const wishlistButtons = document.querySelectorAll(".wishlist");

wishlistButtons.forEach(function (button) {

    button.addEventListener("click", async function () {

        const card = button.closest(".destination-card");
        const destination = card.dataset.destination;

        try {
            const response = await fetch("/toggle-wishlist", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    destination: destination
                })
            });

            const result = await response.json();

            // Login nahi hai
            if (!result.success) {
                alert(result.message);
                return;
            }

            const icon = button.querySelector("i");

            if (result.action === "added") {
                icon.classList.remove("fa-regular");
                icon.classList.add("fa-solid");
                button.classList.add("active");
            } else {
                icon.classList.remove("fa-solid");
                icon.classList.add("fa-regular");
                button.classList.remove("active");
            }

        } catch (error) {
            console.error("Wishlist error:", error);
        }
    });
});

// user rating

const stars = document.querySelectorAll(".interactive-stars i");
const ratingMessage = document.querySelector(".rating-message");
stars.forEach(function (star) {
    star.addEventListener("click", function () {
        const selectedRating = Number(star.dataset.rating);
        stars.forEach(function (currentStar) {
            const starRating = Number(currentStar.dataset.rating);
            if (starRating <= selectedRating) {
             currentStar.classList.remove("fa-regular");
                currentStar.classList.add("fa-solid");
            } else {
            currentStar.classList.remove("fa-solid");
            currentStar.classList.add("fa-regular");
            }
        });

        ratingMessage.textContent ="You rated TravelEase " + selectedRating + " out of 5 stars!";
    });

});
// ḍestinaction explore buttons
// const exploreButtons = document.querySelectorAll(".destination-card .view-btn");

// const detailsSection = document.getElementById("destinationDetails");
// const detailsImage = document.getElementById("detailsImage");
// const detailsLocation = document.getElementById("detailsLocation");
// const detailsName = document.getElementById("detailsName");
// const detailsDescription = document.getElementById("detailsDescription");
// const detailsRating = document.getElementById("detailsRating");

// const destinationData = {
//     Kashmir: {
//         image: "/static/images/kashmir.jpg",
//         location: "Kashmir, India",
//         description: "Experience beautiful mountains, peaceful lakes and breathtaking valleys surrounded by nature.",
//         rating: "4.9"
//     },
//     Dubai: {
//         image: "/static/images/dubai.jpg",
//         location: "Dubai, UAE",
//         description: "Discover luxury, adventure, modern architecture, desert experiences and unforgettable attractions.",
//         rating: "4.8"
//     },
//     Paris: {
//         image: "/static/images/paris.jpg",
//         location: "Paris, France",
//         description: "Explore iconic landmarks, beautiful architecture, rich culture and charming streets of Paris.",
//         rating: "4.9"
//     },
//     Manali: {
//         image: "/static/images/manali.jpg",
//         location: "Manali, India",
//         description: "Enjoy peaceful valleys, snowy mountains, beautiful landscapes and exciting adventures.",
//         rating: "4.7"
//     },
//     Bali: {
//         image: "/static/images/bali.jpg",
//         location: "Bali, Indonesia",
//         description: "Relax on tropical beaches and discover beautiful temples, resorts and island culture.",
//         rating: "4.8"
//     },
//     Switzerland: {
//         image: "/static/images/switzerland.jpg",
//         location: "Switzerland",
//         description: "Experience stunning Alps, peaceful lakes, snowy mountains and charming villages.",
//         rating: "4.9"
//     }
// };

// exploreButtons.forEach(function(button) {
//     button.addEventListener("click", function() {

//         const card = button.closest(".destination-card");

//         const destinationName =
//             card.querySelector("h3").textContent.trim();

//         const destination = destinationData[destinationName];

//         if (!destination) {
//             return;
//         }

//         detailsImage.src = destination.image;
//         detailsImage.alt = destinationName;

//         detailsLocation.textContent = destination.location;

//         detailsName.textContent =destinationName;

//         detailsDescription.textContent =destination.description;
//         detailsRating.textContent = destination.rating;

//         detailsSection.scrollIntoView({
//             behavior: "smooth",
//             block: "start"
//         });
//     });
// });

// Destination Explore Buttons

const exploreButtons = document.querySelectorAll(".destination-card .view-btn");

exploreButtons.forEach(function(button) {

    button.addEventListener("click", function() {

        const card = button.closest(".destination-card");

        const destinationName =
            card.getAttribute("data-destination");

        window.location.href =
            "/destination/" + destinationName;

    });

});

// .ye alag hai
// function openBooking(){
//     window.location.href="/booking";
// }
// Get package details from URL
// const params = new URLSearchParams(window.location.search);

// const packageName = params.get("package");
// const packagePrice = params.get("price");
// const packageDays = params.get("days");

// const nameElement = document.getElementById("packageName");
// const priceElement = document.getElementById("packagePrice");
// const daysElement = document.getElementById("packageDays");

// if (packageName && nameElement) {
//     nameElement.textContent = packageName;
// }

// if (packagePrice && priceElement) {
//     priceElement.textContent = packagePrice;
// }

// if (packageDays && daysElement) {
//     daysElement.textContent = packageDays + " Days";
// }
      const flashMessage = document.querySelector(".flash-message");

if (flashMessage) {
    setTimeout(function () {
        flashMessage.style.display = "none";
    }, 3000);
}