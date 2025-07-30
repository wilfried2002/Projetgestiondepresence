document.addEventListener('DOMContentLoaded', function() {
    const typeField = document.getElementById('id_type');
    const salaireFieldRow = document.querySelector('.form-row.field-salaire_journalier, .form-group.field-salaire_journalier');

    function toggleSalaireField() {
        if (typeField.value === 'temporaire') {
            salaireFieldRow.style.display = '';
        } else {
            salaireFieldRow.style.display = 'none';
        }
    }

    if (typeField && salaireFieldRow) {
        toggleSalaireField();
        typeField.addEventListener('change', toggleSalaireField);
    }
});