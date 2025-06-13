setTimeout(() => {
    const successToast = document.getElementById('toast-success');
    const errorToast = document.getElementById('toast-danger');
    if (successToast){
        successToast.style.display = 'none';
    }

    if (errorToast) {
        errorToast.style.display = 'none';
    }
}, 3000);