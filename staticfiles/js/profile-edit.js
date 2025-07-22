// Email Add/Remove
document.addEventListener('DOMContentLoaded', function () {
    // EMAIL HANDLING
    const emailList = document.getElementById('email-list');
    const addEmailBtn = document.getElementById('add-email-btn');
    const newEmailInput = document.getElementById('new-email-input');
    const emailError = document.getElementById('email-error');

    function validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    addEmailBtn.addEventListener('click', function () {
        console.log("Hi");
        const email = newEmailInput.value.trim();
        if (!email) return;
        if (!validateEmail(email)) {
            emailError.textContent = "Enter a valid email address.";
            return;
        }
        // Check for duplicate
        let isDuplicate = false;
        emailList.querySelectorAll('input[name="emails"]').forEach(function (input) {
            if (input.value.trim().toLowerCase() === email.toLowerCase()) isDuplicate = true;
        });
        if (isDuplicate) {
            emailError.textContent = "This email is already listed.";
            return;
        }
        emailError.textContent = "";
        const emailDiv = document.createElement('div');
        emailDiv.className = 'email-item';
        emailDiv.innerHTML = `
            <input type="email" name="emails" value="${email}" required>
            <button type="button" class="btn-remove-email" aria-label="Remove email">&times;</button>
        `;
        emailList.appendChild(emailDiv);
        newEmailInput.value = "";
    });

    emailList.addEventListener('click', function (e) {
        if (e.target.classList.contains('btn-remove-email')) {
            e.target.parentElement.remove();
        }
    });

    // ADDRESSES HANDLING
    const addressList = document.getElementById('addresses-list');
    const addressEditor = document.getElementById('address-editor');
    const addAddressBtn = document.getElementById('add-address-btn');
    const saveAddressBtn = document.getElementById('save-address-btn');
    const cancelAddressBtn = document.getElementById('cancel-address-btn');
    const addressError = document.getElementById('address-error');

    addAddressBtn.addEventListener('click', () => {
        // display cleared editor
        addressEditor.style.display = "block";
        inputs = addressEditor.getElementsByTagName('input');
        for (const i of inputs) {
            i.value = "";
        }
    });

    saveAddressBtn.addEventListener('click', () => {
        // 1. Get the field values and trim whitespace
        const street = document.getElementById('addr_street').value.trim();
        const city = document.getElementById('addr_city').value.trim();
        const state = document.getElementById('addr_state').value.trim();
        const postal = document.getElementById('addr_postal').value.trim();
        const country = document.getElementById('addr_country').value.trim();

        // 2. Validate non-empty fields
        if (!street || !city || !state || !postal || !country) {
            addressError.textContent = "All address fields are required.";
            return;
        }

        addressError.textContent = ""; // Clear error

        addAddress(street, city, state, postal, country);

        addressEditor.style.display = "None";

    });

    cancelAddressBtn.addEventListener('click', () => {
        addressEditor.style.display = "none";
        inputs = addressEditor.getElementsByTagName('input');
        for (const i of inputs) {
            i.value = "";
        }

    });

    let editingCard = null;
    addressList.addEventListener('click', (e) => {
        if (e.target.classList.contains('btn-edit-address')) {
            let card = e.target.closest('.address-card');
            editingCard = card;

            const hiddenInput = card.getElementsByTagName('input')[0];
            const [street, city, state, postal, country] = hiddenInput.value.split('|');

            // display cleared editor
            addressEditor.style.display = "block";
            inputs = addressEditor.getElementsByTagName('input');
            for (const i of inputs) {
                i.value = "";
            }

            document.getElementById('addr_street').value = street;
            document.getElementById('addr_city').value = city;
            document.getElementById('addr_state').value = state;
            document.getElementById('addr_postal').value = postal;
            document.getElementById('addr_country').value = country;

        }
    });

    addressList.addEventListener('click', (e) => {
         if (e.target.classList.contains('btn-remove-address')) {
            let card = e.target.closest('.address-card');
            card.remove();
         }
    });

    // INTENT COUNTER
    const intent = document.getElementById('intent');
    const intentCount = document.getElementById('intent-count');
    if (intent && intentCount) {
        intentCount.textContent = intent.value.length;
        intent.addEventListener('input', function () {
            intentCount.textContent = intent.value.length;
        });
    }

    // FORM EVENT HANDLER
    const form = document.getElementById('profile-form');
    form.addEventListener('submit', (event) => {
        if (emailList.getElementsByTagName('input').length == 0) {
            emailError.textContent = "At least one email is required.";
            event.preventDefault();
        }
    });
});


function addAddress(street, city, state, postal, country) {
    const card = document.createElement('div');
    card.className = 'address-card';

    // Address fields div
    const fieldsDiv = document.createElement('div');
    fieldsDiv.className = 'address-fields';

    const spanStreet = document.createElement('span');
    spanStreet.className = 'address-line';
    spanStreet.textContent = street;

    const spanCity = document.createElement('span');
    spanCity.className = 'address-line';
    spanCity.textContent = city;

    const spanState = document.createElement('span');
    spanState.className = 'address-line';
    spanState.textContent = state;

    const spanPostal = document.createElement('span');
    spanPostal.className = 'address-line';
    spanPostal.textContent = postal;

    const spanCountry = document.createElement('span');
    spanCountry.className = 'address-line';
    spanCountry.textContent = country;

    // Add spans (and commas, as text nodes)
    fieldsDiv.appendChild(spanStreet);
    fieldsDiv.appendChild(document.createTextNode(', '));
    fieldsDiv.appendChild(spanCity);
    fieldsDiv.appendChild(document.createTextNode(', '));
    fieldsDiv.appendChild(spanState);
    fieldsDiv.appendChild(document.createTextNode(' '));
    fieldsDiv.appendChild(spanPostal);
    fieldsDiv.appendChild(document.createTextNode(', '));
    fieldsDiv.appendChild(spanCountry);

    card.appendChild(fieldsDiv);

    // Actions div
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'address-actions';

    const editBtn = document.createElement('button');
    editBtn.type = 'button';
    editBtn.className = 'btn-edit-address';
    editBtn.setAttribute('aria-label', 'Edit address');
    editBtn.textContent = 'Edit';

    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'btn-remove-address';
    removeBtn.setAttribute('aria-label', 'Remove address');
    removeBtn.textContent = '×';

    actionsDiv.appendChild(editBtn);
    actionsDiv.appendChild(removeBtn);

    card.appendChild(actionsDiv);

    // Hidden input for backend
    const hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = 'addresses';
    hiddenInput.value = [street, city, state, postal, country].join('|');

    card.appendChild(hiddenInput);

    // Add to DOM
    document.getElementById('addresses-list').appendChild(card);
}