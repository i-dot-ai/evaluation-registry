const isFinalReportPublishedRadios = document.forms["share-evaluation-form"].elements["is_final_report_published"];
const plan_link = document.getElementById("plan_link-form-group");
const link_to_published_evaluation = document.getElementById("link_to_published_evaluation-form-group");
const reasons_unpublished = document.getElementById("reasons_unpublished-form-group");

function changeVisibility(checkedValue) {
    if (checkedValue === "0") {
        plan_link.classList.add("govuk-!-display-none");
        link_to_published_evaluation.classList.add("govuk-!-display-none");
        reasons_unpublished.classList.remove("govuk-!-display-none");
    } else if (checkedValue === "1") {
        plan_link.classList.remove("govuk-!-display-none");
        link_to_published_evaluation.classList.remove("govuk-!-display-none");
        reasons_unpublished.classList.add("govuk-!-display-none");
    }
}

if (isFinalReportPublishedRadios) {
    for(let i = 0, max = isFinalReportPublishedRadios.length; i < max; i++) {
        isFinalReportPublishedRadios[i].onchange = function() { changeVisibility(this.value) }
    }
}
