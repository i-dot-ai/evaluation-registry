// From github.com/alphagov/govuk_publishing_components/ file app/assets/javascripts/govuk_publishing_components/components/option-select.js

window.GOVUK = window.GOVUK || {}
window.GOVUK.Modules = window.GOVUK.Modules || {};

(function (Modules) {
  /* This JavaScript provides two functional enhancements to option-select components:
    1) A count that shows how many results have been checked in the option-container
    2) Open/closing of the list of checkboxes
  */
  function OptionSelect ($module) {
    this.$optionSelect = $module
    this.$options = this.$optionSelect.querySelectorAll("input[type='checkbox']")
    this.$optionsContainer = this.$optionSelect.querySelector('.autofilter-option-select__container')
    this.$optionList = this.$optionsContainer.querySelector('.js-auto-height-inner')
    this.$allCheckboxes = this.$optionsContainer.querySelectorAll('.govuk-checkboxes__item')
    this.filterLabel = this.$optionSelect.getAttribute('data-filter-element') || ''


    this.checkedCheckboxes = []
  }

  OptionSelect.prototype.init = function () {
    if (this.filterLabel.length) {

      var filterEl = document.createElement('div')
      var label = document.createElement('label')
      label.for = `input-${this.filterLabel}`
      label.classList = ['govuk-label govuk-visually-hidden']
      label.textContent = this.filterLabel

      var input = document.createElement('input')
      input.name='option-select-filter'
      input.id = `input-${this.filterLabel}`
      input.classList = ['autofilter-option-select__filter-input govuk-input']
      input.type = 'text'
      input.setAttribute('aria-describedby', 'checkboxes-filter-department-count')
      input.setAttribute('aria-controls', 'checkboxes-filter-department-count')
      
      filterEl.appendChild(label)
      filterEl.appendChild(input)

      var optionSelectFilter = filterEl.cloneNode(true)
      optionSelectFilter.classList.add('autofilter-option-select__filter')


      this.$optionsContainer.parentNode.insertBefore(optionSelectFilter, this.$optionsContainer)

      this.$filter = this.$optionSelect.querySelector('input[name="option-select-filter"]')

      this.$filterCount = document.getElementById(this.$filter.getAttribute('aria-describedby'))
      this.filterTextSingle = ' ' + this.$filterCount.getAttribute('data-single')
      this.filterTextMultiple = ' ' + this.$filterCount.getAttribute('data-multiple')
      this.filterTextSelected = ' ' + this.$filterCount.getAttribute('data-selected')
      this.checkboxLabels = []
      this.filterTimeout = 0

      this.getAllCheckedCheckboxes()
      for (var i = 0; i < this.$allCheckboxes.length; i++) {
        this.checkboxLabels.push(this.cleanString(this.$allCheckboxes[i].textContent))
      }

      this.$filter.addEventListener('keyup', this.typeFilterText.bind(this))
    }

    // Attach listener to update checked count
    this.$optionsContainer.querySelector('.autofilter-checkboxes__list').addEventListener('change', this.updateCheckedCount.bind(this))

    var checkedString = this.checkedString()
    if (checkedString) {
      this.attachCheckedCounter(checkedString)
    }
  }

  OptionSelect.prototype.typeFilterText = function (event) {
    event.stopPropagation()
    var ENTER_KEY = 13

    if (event.keyCode !== ENTER_KEY) {
      clearTimeout(this.filterTimeout)
      this.filterTimeout = setTimeout(
        function () { this.doFilter(this) }.bind(this),
        300
      )
    } else {
      event.preventDefault() // prevents finder forms from being submitted when user presses ENTER
    }
  }

  OptionSelect.prototype.cleanString = function cleanString (text) {
    text = text.replace(/&/g, 'and')
    text = text.replace(/[’',:–-]/g, '') // remove punctuation characters
    text = text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') // escape special characters
    return text.trim().replace(/\s\s+/g, ' ').toLowerCase() // replace multiple spaces with one
  }

  OptionSelect.prototype.getAllCheckedCheckboxes = function getAllCheckedCheckboxes () {
    this.checkedCheckboxes = []

    for (var i = 0; i < this.$options.length; i++) {
      if (this.$options[i].checked) {
        this.checkedCheckboxes.push(i)
      }
    }
  }

  OptionSelect.prototype.doFilter = function doFilter (obj) {
    var filterBy = obj.cleanString(obj.$filter.value)
    var showCheckboxes = obj.checkedCheckboxes.slice()
    var i = 0

    for (i = 0; i < obj.$allCheckboxes.length; i++) {
      if (showCheckboxes.indexOf(i) === -1 && obj.checkboxLabels[i].search(filterBy) !== -1) {
        showCheckboxes.push(i)
      }
    }

    for (i = 0; i < obj.$allCheckboxes.length; i++) {
      obj.$allCheckboxes[i].style.display = 'none'
    }

    for (i = 0; i < showCheckboxes.length; i++) {
      obj.$allCheckboxes[showCheckboxes[i]].style.display = 'block'
    }

    var lenChecked = obj.$optionsContainer.querySelectorAll('.govuk-checkboxes__input:checked').length
    var len = showCheckboxes.length + lenChecked
    var html = len + (len === 1 ? obj.filterTextSingle : obj.filterTextMultiple) + ', ' + lenChecked + obj.filterTextSelected
    obj.$filterCount.textContent(html)
  }

  OptionSelect.prototype.attachCheckedCounter = function attachCheckedCounter (checkedString) {
    var element = document.createElement('div')
    element.setAttribute('class', 'autofilter-option-select__selected-counter js-selected-counter')
    element.textContent(checkedString)
    this.$optionSelect.querySelector('.autofilter-legend').insertAdjacentElement('afterend', element)
  }

  OptionSelect.prototype.updateCheckedCount = function updateCheckedCount () {
    var checkedString = this.checkedString()
    var checkedStringElement = this.$optionSelect.querySelector('.js-selected-counter')

    if (checkedString) {
      if (checkedStringElement === null) {
        this.attachCheckedCounter(checkedString)
      } else {
        checkedStringElement.textContent = checkedString
      }
    } else if (checkedStringElement) {
      checkedStringElement.parentNode.removeChild(checkedStringElement)
    }
  }

  OptionSelect.prototype.checkedString = function checkedString () {
    this.getAllCheckedCheckboxes()
    var count = this.checkedCheckboxes.length
    var checkedString = false
    if (count > 0) {
      checkedString = count + ' selected'
    }

    return checkedString
  }


  Modules.OptionSelect = OptionSelect
})(window.GOVUK.Modules)

var a = new window.GOVUK.Modules.OptionSelect(document.getElementById('autofilter'))
a.init()
