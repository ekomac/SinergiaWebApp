$(document).ready(function () {

    //Get the button:
    backToTopBtn = document.getElementById("backToTopBtn");

    // When the user scrolls down 20px from the top of the document, show the button
    window.onscroll = function () {
        scrollFunction()
    };

    $("#not-header").scroll(function () {
        if ($(this).scrollTop() >= 20) {
            backToTopBtn.style.display = "block";
        } else {
            backToTopBtn.style.display = "none";
        }
    });

    function scrollFunction() {
        if (document.body.scrollTop > 10 || document.documentElement.scrollTop > 10) {
            backToTopBtn.style.display = "block";
        } else {
            backToTopBtn.style.display = "none";
        }
    }
});

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
    // $("#not-header").scrollTop(0);
    document.getElementById("not-header").scrollTo({ top: 0, behavior: 'smooth' });
    document.body.scrollTop = 0; // For Safari
    document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}

/**
 * When toast "close" button is pressed, to dismiss the alert.
 * 
 * @param {string} post_url: Django url to dismiss the alert.
 * @returns 
 */
function dismissAlert(post_url) {
    $.ajax({
        url: post_url,
        type: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        dataType: "json",
        data: {},
        processData: false,
        contentType: false,
    });
    return false;
}

/**
 * Retrieves cookie from broswer.
 */
function getCookie(c_name) {
    /* If it has a cookie */
    if (document.cookie.length > 0) {
        // Get the cookie for provided c_name
        c_start = document.cookie.indexOf(c_name + "=");
        // If cookie exists
        if (c_start != -1) {
            // Sets start index to next char from "="
            c_start = c_start + c_name.length + 1;
            // Sets the end index to first index of ";" since start
            c_end = document.cookie.indexOf(";", c_start);
            // If end existes, end is the length of the cookie
            if (c_end == -1) c_end = document.cookie.length;

            // Return the substring from start and end index
            return decodeURI(document.cookie.substring(c_start, c_end));
        }
    }
    return "";
}

function enableTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
}