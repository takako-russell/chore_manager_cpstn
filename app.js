document.addEventListener("DOMContentLoaded", () => {
    let table = getElementByID("calendar-table");

    table.addEventListener('click', (e) => {
        let clickedCell = e.target;
        if(clickedCell.tagName === 'TD') {
            
        }
    })
})