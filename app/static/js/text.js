var createDivButton = document.getElementById('createDivButton');
var dsLieuLuongThuoc = document.querySelector("#dsLieuLuongThuoc");
var motLoaiThuoc = document.querySelector(".motLoaiThuoc");
var array_motLoaiThuoc = document.querySelectorAll('.motLoaiThuoc')
var array_deleteDivButton = document.querySelectorAll('.deleteDivButton')
var array_deleteDiv = document.querySelectorAll('.deleteDiv')

array_deleteDiv[0].classList.add('hide')

createDivButton.addEventListener('click',function () {

    if(array_deleteDiv.length === 1) {
        array_deleteDiv[0].classList.remove('hide')
        addMotLoaiThuoc()
        array_deleteDiv[0].classList.add('hide')
    }else {
        addMotLoaiThuoc()
    }
});

function addMotLoaiThuoc() {
        let clonedDiv = motLoaiThuoc.cloneNode(true);
        dsLieuLuongThuoc.appendChild(clonedDiv)
        array_motLoaiThuoc = document.querySelectorAll('.motLoaiThuoc')
        dsLieuLuongThuoc = document.querySelector("#dsLieuLuongThuoc")
        array_deleteDivButton = document.querySelectorAll('.deleteDivButton')

        for (let i = 0 ; i < array_deleteDivButton.length ; i++){
        array_deleteDivButton[i].addEventListener('click',function () {
             let elementToRemove = array_motLoaiThuoc[i]
             elementToRemove.remove()
        });
   }
}



