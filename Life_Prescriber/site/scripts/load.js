// THIS IS FOR THE LOADING PAGE

window.addEventListener('load', function () {

    const logo = document.getElementById('loading-logo');
    const logo1 = document.getElementById('loading-logo2')

    var loadingScreen1 = document.getElementById('loading1');
    loadingScreen1.style.display = 'none';


    // Fading in of the logo
    setTimeout(() => {
        logo.style.opacity = 1;
    }, 500);



    // Starting fadding # out
    setTimeout(() => {

        const loadingScreen = document.getElementById('loading');
        loadingScreen.style.opacity = 0;
        loadingScreen.style.transition = 'opacity 2.5s ease-in-out';
    }, 3000);



    // Removoving the loading page
    setTimeout(() => {
        const loadingScreen = document.getElementById('loading');
        loadingScreen.style.display = 'none';

        loadingScreen1 = document.getElementById('loading1')
        loadingScreen1.style.display = "flex"




        // Opening the sign up or sign in page
        setTimeout(() => {
            window.location.href = '/prescription_ongo/custom_login/';
        }, 2000);

    }, 5600);


});