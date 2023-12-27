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

array_loaithuoc = document.querySelectorAll('.loaithuoc')
array_donvithuoc = document.querySelectorAll('.donvithuoc')
document.getElementById("lpk_form").addEventListener("submit", function(event) {

    let values = [];

    array_loaithuoc = document.querySelectorAll('.loaithuoc')

    // Lặp qua từng phần tử và lấy giá trị
    array_loaithuoc.forEach(function(element) {
        values.push(element.value);
    });

    let uniqueStrings = countUniqueStrings(values)

    if (uniqueStrings < array_loaithuoc.length) {

        console.log(values)
        console.log(array_loaithuoc.length)
        // Ngăn chặn submit form
        event.preventDefault();

        alert("Trùng lặp thông tin về loại thuốc!");
    } else {
        // Không có lỗi, cho phép submit form
        // (mặc định, sự kiện sẽ tiếp tục và form sẽ được submit)
    }
});

function countUniqueStrings(arr) {
    // Sử dụng một đối tượng để theo dõi giá trị duy nhất
    var uniqueStrings = {};

    // Lặp qua từng phần tử trong mảng
    for (var i = 0; i < arr.length; i++) {
        // Kiểm tra xem phần tử có phải là chuỗi không
        if (typeof arr[i] === 'string') {
            // Gán giá trị là true cho phần tử trong đối tượng uniqueStrings
            uniqueStrings[arr[i]] = true;
        }
    }

    // Đếm số lượng khóa (giá trị duy nhất) trong đối tượng
    var count = Object.keys(uniqueStrings).length;

    return count;
}
