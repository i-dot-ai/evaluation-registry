import './style/main.scss'
import accessibleAutocomplete from 'accessible-autocomplete'
import { initAll } from 'govuk-frontend'

initAll()

window.addEventListener('load', (event) => {

  const autocompleteElements = document.querySelectorAll('[data-accessible-autocomplete]')

  autocompleteElements.forEach(value => {
    accessibleAutocomplete.enhanceSelectElement({
      selectElement: value
    })
  })

  // for(el in autocompleteElements) {
  //   console.log(el)
  //   accessibleAutocomplete.enhanceSelectElement({
  //     selectElement: el
  //   })
  // }
});
