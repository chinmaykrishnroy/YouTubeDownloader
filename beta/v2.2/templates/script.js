window.onload = function () {
    var sidebar = document.getElementById('sidebar');
    var sidebarbutton = sidebar.getElementsByTagName('sidebar-button');
    for (var i = 0; i < sidebarbutton.length; i++) {
        Tbutton[i].style.display = 'none'; // Hide the buttons
    }
};

function toggleMenu() {
    var sidebar = document.getElementById('sidebar');
    var searchspace = document.getElementById('searchspace');
    var downloadspace = document.getElementById('downloadspace');
    var Tbutton = document.getElementById('button');
    var sidebarbutton = sidebar.querySelectorAll('sidebar-button');

    // Toggle the 'active' class on the menu and main content
    sidebar.classList.toggle('active');
    searchspace.classList.toggle('active');
    downloadspace.classList.toggle('active');

    // Check if the menu is active or not
    if (sidebar.classList.contains('active')) {
        // Menu is active, show the buttons
        sidebarbutton.forEach(function (button) {
            button.style.display = 'block';
        });
        Tbutton.innerHTML = 'created by Chinmay Roy';

    } else {
        // Menu is not active, hide the buttons
        sidebarbutton.forEach(function (button) {
            button.style.display = 'none';
        });
        Tbutton.innerHTML = '☰';
    }
};