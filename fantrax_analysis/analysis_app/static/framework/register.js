/* Because i didnt set placeholder values in forms.py they will be set here using vanilla Javascript
		//We start indexing at one because CSRF_token is considered and input field
		 */
$(document).ready(function(){
    //Query All input fields
    var form_fields = document.getElementsByTagName('input');

    console.log('form field', form_fields);
    form_fields[0].placeholder='Username..';
    form_fields[1].placeholder='Email..';
    form_fields[2].placeholder='Enter password...';
    form_fields[3].placeholder='Re-enter Password...';


    for (var field in form_fields){
        form_fields[field].className += ' form-control'
    }
})

