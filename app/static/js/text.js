var createDivButton = document.getElementById("createDivButton");
var dsLieuLuongThuoc = document.querySelector("#dsLieuLuongThuoc");
var motLoaiThuoc = document.querySelector(".motLoaiThuoc");
var array_motLoaiThuoc = document.querySelectorAll('.motLoaiThuoc')
var array_deleteDivButton = document.querySelectorAll('.deleteDivButton')
createDivButton.addEventListener('click',function () {
    addMotLoaiThuoc()
});

function addMotLoaiThuoc() {
        // Tạo một phần tử div mới
        var clonedDiv = motLoaiThuoc.cloneNode(true);
        dsLieuLuongThuoc.appendChild(clonedDiv);
        array_motLoaiThuoc = document.querySelectorAll('.motLoaiThuoc')
        dsLieuLuongThuoc = document.querySelector("#dsLieuLuongThuoc")
        array_deleteDivButton = document.querySelectorAll('.deleteDivButton')
}


// document.addEventListener('DOMContentLoaded', function() {
//     // Lấy tất cả các phần tử có class "delete"
//     array_deleteDivButton = dsLieuLuongThuoc.querySelectorAll('.deleteDivButton')
//
//     // Gắn sự kiện click cho mỗi nút "delete"
//     array_deleteDivButton.forEach(function(button, index) {
//       button.addEventListener('click', function() {
//         // Thực hiện các hành động khi nút "delete" được click
//         console.log('Clicked on delete button ' + (index + 1));
//       });
//     });
//     dsLieuLuongThuoc = document.querySelector("#dsLieuLuongThuoc");
//     array_deleteDivButton = dsLieuLuongThuoc.querySelectorAll('.deleteDivButton')
//   });

for (let i = 0; i < array_deleteDivButton.length; i++) {
    array_deleteDivButton = document.querySelectorAll('.deleteDivButton')

    array_deleteDivButton[i].onclick = function() {
         console.log('Clicked on delete button ' + (i + 1));
    }
}

