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
