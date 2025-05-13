//------------------------------------------Declaring Array--------------------------------------------
var arr = [];
//------------------------------------------global variable --------------------------------------------
var insertHere = document.getElementById("data-host");
var editableIndex = null;

var is_editing = false;

//------------------------------------getting all inpputs from HTML------------------------------------
function data_getObject() {
    var username = document.getElementById("inpName");
    var fname = document.getElementById("inpFName");
    var email = document.getElementById("inpEmail");
    var number = document.getElementById("inpNumber");
    var gender = document.querySelector('input[name="gender"]:checked');
    var address = document.getElementById("inpAddress");
    var date = document.getElementById("inpDate");
    var country = document.getElementById("inpCountry");
    var province = document.getElementById("inpProvince");
    var course = document.getElementById("inpCourse");

    var studObj = {
        st_name: username.value,
        st_father: fname.value,
        st_email: email.value,
        st_number: number.value,
        st_gender: gender.value,
        st_address: address.value,
        st_date: date.value,
        st_country: country.value,
        st_province: province.value,
        st_course: course.value,
    }
    if (
        username.value == "" ||
        fname.value == "" ||
        email.value == "" ||
        number.value == "" ||
        gender.value == "" ||
        address.value == "" ||
        date.value == "" ||
        country.value == "" ||
        province.value == "" ||
        course.value == ""
    ) {
        alert("Please fill all the inputs first")
    }
    else if (editableIndex != null) {
        var getting = localStorage.getItem("form-data");
        console.log(getting);
        let j = JSON.parse(getting);
        j.splice(editableIndex, 1, studObj);
        localStorage.setItem("form-data", JSON.stringify(j));

        editableIndex = null;
        window.open("./enrolled_students.html");
    }
    else {
        var getting = localStorage.getItem("form-data");
        let j = JSON.parse(getting);
        j.push(studObj);
        localStorage.setItem("form-data", JSON.stringify(j));
        data_structure_creation();
        window.open("./enrolled_students.html");
    }
}
//--------------------------------------submit on enter key function--------------------------------------
var variable = document.getElementById("inpCourse");
if (variable) {
    variable.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            document.getElementById("submit").click();
        }
        else {
            console.log("Error")
        }
    })
}
//------------------------------------------submit button click-----------------------------------------------  
var variable2 = document.getElementById("submit");
if (variable2) {
    variable2.addEventListener("click", function (event) {
        event.preventDefault();
        data_getObject()
    });
}
//------------------------------------------function to print data-----------------------------------------------  
function data_structure_creation() {
    if(insertHere){
        insertHere.innerHTML = "";
    
        var getting = localStorage.getItem("form-data");
        console.log(getting);
        let j = JSON.parse(getting);
    
        j.forEach(function (studObj, i) {
            insertHere.innerHTML +=
                "<tr>"
                + "<td>" + studObj.st_name + "</td>"
                + "<td>" + studObj.st_father + "</td>"
                + "<td>" + studObj.st_email + "</td>"
                + "<td>" + studObj.st_number + "</td>"
                + "<td>" + studObj.st_gender + "</td>"
                + "<td>" + studObj.st_address + "</td>"
                + "<td>" + studObj.st_date + "</td>"
                + "<td>" + studObj.st_country + "</td>"
                + "<td>" + studObj.st_province + "</td>"
                + "<td>" + studObj.st_course + "</td>"
                + "<td class='btn-host'>"
                // + "<button id='edit'>"< + "Edit" + "</button>"
                + "<a href='./edit-enrolled.html#" + i + "' id='edit'>Edit</a>"
                + "<button id='delete' onclick = 'delThis(" + i + ")'>" + "Delete" + "</button>"
                + "</td>" +
                "</tr>"
        });
    }
}
//------------------------------------------function to edit data-----------------------------------------------  
function edit(i) {

    var getting = localStorage.getItem("form-data");
    // console.log(getting);
    var j = JSON.parse(getting);

    studObj = j[i];
    editableIndex = i;

    var username = document.getElementById("inpName");
    var fname = document.getElementById("inpFName");
    var email = document.getElementById("inpEmail");
    var number = document.getElementById("inpNumber");
    var gender = document.querySelector('input[name="gender"]');
    console.log(gender);
    var address = document.getElementById("inpAddress");
    var date = document.getElementById("inpDate");
    var country = document.getElementById("inpCountry");
    var province = document.getElementById("inpProvince");
    var course = document.getElementById("inpCourse");

    if(studObj){
        if (username) {
            username.value = studObj.st_name;
        }
        if (fname) {
            fname.value = studObj.st_father;
        } if (email) {
            email.value = studObj.st_email;
        } if (number) {
            number.value = studObj.st_number;
        } if (gender) {
            gender.checked.value = studObj.st_gender;
        } if (address) {
            address.value = studObj.st_address;
        } if (date) {
            date.value = studObj.st_date;
        } if (country) {
            country.value = studObj.st_country;
        } if (province) {
            province.value = studObj.st_province;
        } if (course) {
            course.value = studObj.st_course;
        }
    }
}
function delThis(i) {

    var getting = localStorage.getItem("form-data");
    console.log(getting);
    var j = JSON.parse(getting);

    j.splice(i, 1);
    localStorage.setItem("form-data", JSON.stringify(j));
    data_structure_creation();
}
// ------------------------------------function for search data---------------------------------------
function searchTask() {
    var filter, data, tbr, ai, i, txtValue;


    tosearch = document.getElementById("serinput");
    filter = tosearch.value.toUpperCase();
    data = document.getElementById("data-host");
    tbr = data.getElementsByTagName("tr");
    for (i = 0; i < tbr.length; i++) {
        ai = tbr[i].getElementsByTagName("td")[0];
        txtValue = ai.textContent || ai.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            tbr[i].style.display = "";
        } else {
            tbr[i].style.display = "none";
        }
        console.log(txtValue);
    }
}

window.onload = () => {
    data_structure_creation();
    var u = document.URL.split("#");
    console.log(u[1]);
    console.log(document.URL);
    if(u[1] !== ""){
        edit(u[1]);
    }
    else{
        return null;
    }
}