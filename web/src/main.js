import './style/main.scss'
import accessibleAutocomplete from 'accessible-autocomplete'
import DOMPurify from 'dompurify';
import { initAll } from 'govuk-frontend'

window.addEventListener('load', (event) => {
  // from https://web.dev/articles/trusted-types
  if (window.trustedTypes && trustedTypes.createPolicy) {
    trustedTypes.createPolicy('default', {
      createHTML: (string, sink) => DOMPurify.sanitize(string, {RETURN_TRUSTED_TYPE: true})
    });
  }

  initAll()

  const autocompleteElements = document.querySelectorAll('[data-accessible-autocomplete]')

  autocompleteElements.forEach(value => {
    accessibleAutocomplete.enhanceSelectElement({
      selectElement: value
    })
  })
});

const isFinalReportPublishedRadios = document.forms["share-evaluation-form"]?.elements["is_final_report_published"];
const reasonsUnpublishedCheckboxes = document.forms["share-evaluation-form"]?.elements["reasons_unpublished"];
const plan_link = document.getElementById("plan_link-form-group");
const link_to_published_evaluation = document.getElementById("link_to_published_evaluation-form-group");
const reasons_unpublished = document.getElementById("reasons_unpublished-form-group");
const reasons_unpublished_details = document.getElementById("reasons_unpublished_details-form-group");

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

function showHideReasonDetails() {
    const selectedCheckboxes = Array.from(reasonsUnpublishedCheckboxes).filter(checkbox => checkbox.checked);
    const selectedValues = selectedCheckboxes.map(checkbox => checkbox.value);
    const valuesWithOther = ["other", "quality"]
    if (valuesWithOther.some(v => selectedValues.includes(v))) {
        reasons_unpublished_details.classList.remove("govuk-!-display-none");
    }
    else {
        reasons_unpublished_details.classList.add("govuk-!-display-none");
    }
}

if (isFinalReportPublishedRadios) {
    for(let i = 0, max = isFinalReportPublishedRadios.length; i < max; i++) {
        isFinalReportPublishedRadios[i].onchange = function() { changeVisibility(this.value) }
    }
}

if (reasonsUnpublishedCheckboxes) {
    for(let i = 0, max = reasonsUnpublishedCheckboxes.length; i < max; i++) {
        reasonsUnpublishedCheckboxes[i].onchange = function() { showHideReasonDetails(this.value) }
    }
}
