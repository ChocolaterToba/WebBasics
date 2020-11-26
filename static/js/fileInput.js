function getFile(id) {
    document.getElementById(id).click();
}
  
function sub(obj, id) {
    var file = obj.value;
    var fileName = file.split("\\");
    document.getElementById(id).innerHTML = fileName[fileName.length - 1];
    event.preventDefault();
}
