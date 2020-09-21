function toggleTheme() {
    curr_theme = localStorage.getItem('theme');
    if (curr_theme && curr_theme == 'light') {
        localStorage.setItem('theme', 'dark');
    } else {
        localStorage.setItem('theme', 'light');
    }
    checkTheme();
    checkIcons();
};

function checkTheme() {
    curr_theme = localStorage.getItem('theme');
    style = document.getElementById('style');
    if (curr_theme && curr_theme == 'light') {
        style.href = (style.href).replace('dark', 'light');
    } else if (curr_theme && curr_theme == 'dark') {
        style.href = (style.href).replace('light', 'dark');
    }
}

function checkIcons() {
    curr_theme = localStorage.getItem('theme');
    checkbox = document.getElementById("theme");
    logo = document.getElementById('logo');
    if (curr_theme && curr_theme == 'light') {
        logo.src = (logo.src).replace('dark', 'light');
        checkbox.checked = false;
    } else if (curr_theme && curr_theme == 'dark') {
        logo.src = (logo.src).replace('light', 'dark');
        checkbox.checked = true;
    }
    checkActions();
}

function checkActions() {
    curr_theme = localStorage.getItem('theme');
    edit_action = document.getElementsByClassName('viewPost-edit-button');
    delete_actions = document.getElementsByClassName('viewPost-delete-button');
    if (curr_theme && curr_theme == 'light') {
        action = edit_action.item(0);
        if (action) {
            action.src = (action.src).replace('dark', 'light');
        }
        for (i = 0; i < delete_actions.length; i++) {
            action = delete_actions.item(i);
            action.src = (action.src).replace('dark', 'light');
        }
    } else if (curr_theme && curr_theme == 'dark') {
        action = edit_action.item(0);
        if (action) {
            action.src = (action.src).replace('light', 'dark');
        }
        for (i = 0; i < delete_actions.length; i++) {
            action = delete_actions.item(i);
            action.src = (action.src).replace('light', 'dark');
        }
    }
}

function modalComment(c_id) {
    document.getElementById('comment_id').value = c_id;
    document.getElementById('comment-modal').style.display = 'flex';
};

checkTheme();
window.onload = checkIcons;