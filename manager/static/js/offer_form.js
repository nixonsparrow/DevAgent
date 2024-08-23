function companySwitcher(element_id) {
    element = document.getElementById(element_id);

    function getAnotherId() {
        if (element_id.includes("new")) {
            return "_company";
        } else {
            return "_new_company";
        };
    };

    another_element = document.getElementById(getAnotherId());

    element.classList.add("bg-steel");
    another_element.classList.remove("bg-steel");
    document.getElementById("id" + element_id).setAttribute("required", "");
    document.getElementById("id" + getAnotherId()).removeAttribute("required");
    document.getElementById("div_id" + element_id).classList.remove("hide");
    document.getElementById("div_id" + getAnotherId()).classList.add("hide");
}
var init_div_new_company = document.getElementById("div_id_new_company");
init_div_new_company.removeAttribute("required");
init_div_new_company.classList.add("hide");
document.getElementById("switcher").classList.remove("hide");

document.getElementById("_new_company").click();
document.getElementById("_company").click();