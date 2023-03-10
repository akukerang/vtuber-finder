const tagContainer = document.querySelector('.tag-container');
const input = document.querySelector('.tag-container input');
var tags = [];

function createTag(label){
    const div = document.createElement('div');
    div.setAttribute('class','tag');

    const span = document.createElement('span');
    span.innerHTML = label;

    const close = document.createElement('i');
    close.setAttribute('class','material-icons');
    close.setAttribute('data-item',label);
    close.innerHTML = 'close';

    div.appendChild(span);
    div.appendChild(close);
    return div;
}

function reset() {
    document.querySelectorAll('.tag').forEach(function(tag) {
        tag.parentElement.removeChild(tag);
    })
}

function addTags() {
    reset();
    tags.forEach(
        function(tag){
            const input = createTag(tag);
            tagContainer.prepend(input);
        }
    )
}

input.addEventListener('keydown', function(e) {
    if(e.key == 'Enter' && input.value != ''){
        tags.unshift(input.value);
        addTags();
        input.value = '';
    } else if(e.key == ',' && input.value != '' && input.value != ','){
        tags.unshift(input.value.slice(0,input.value.indexOf('-')));
        addTags();
        input.value = '';
    } else if (e.key == 'Backspace'){
        if(input.value == ''){
            tags = [...tags.slice(1)];
            addTags();
        }
    }
})

document.addEventListener('click', function(e){
    if(e.target.tagName == 'I'){
        const value = e.target.getAttribute('data-item');
        const index = tags.indexOf(value);
        tags = [...tags.slice(0,index),...tags.slice(index+1)];
        addTags();
    }
})


function getLanguage(){
    var languages = [];
    var checkboxes = document.querySelectorAll('.checkbox:checked');
    checkboxes.forEach((checkbox)=> {
        languages.push(checkbox.value)
    })
    return languages;
}

function setChecked(languages){
    var checkboxes = document.querySelectorAll('.checkbox');
    checkboxes.forEach((checkbox)=> {
        if(languages.includes(checkbox.value)) {checkbox.checked=true}
    })
}

function sendData(){
    location.href = `/sendkeywords?data=${tags}&languages=${getLanguage()}`;
}

