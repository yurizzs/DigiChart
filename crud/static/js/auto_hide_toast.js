setTimeout(() => {
    const successToast = document.getElementById('toast-success');
    const errorToast = document.getElementById('toast-error')

    if (successToast){
        successToast.style.display = 'none';
    }

    if (errorToast) {
        errorToast.style.display = 'none';
    }
}, 3000);