document.getElementById('uploadFileButton').addEventListener('click', () => {
    document.getElementById('fileInput').click();
});

document.getElementById('uploadFolderButton').addEventListener('click', () => {
    document.getElementById('folderInput').click();
});

document
    .getElementById('fileInput')
    .addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('description', 'Uploaded file');
            formData.append('file', file);

            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData,
                });
                const result = await response.json();
                alert(`File uploaded successfully: ${JSON.stringify(result)}`);
            } catch (error) {
                alert('Error uploading file');
            }
        }
    });

document
    .getElementById('folderInput')
    .addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('description', 'Uploaded folder');
            formData.append('file', file);

            try {
                const response = await fetch('/upload-folder', {
                    method: 'POST',
                    body: formData,
                });
                const result = await response.json();
                alert(
                    `Folder uploaded successfully: ${JSON.stringify(result)}`
                );
            } catch (error) {
                alert('Error uploading folder');
            }
        }
    });
