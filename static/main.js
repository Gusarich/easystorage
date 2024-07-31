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
            formData.append('description', file.name); // Pass the filename as description
            formData.append('file', file);

            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData,
                });
                const result = await response.json();
                displayBagId(result.bag_id);
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
            formData.append('description', file.name); // Pass the filename as description
            formData.append('file', file);

            try {
                const response = await fetch('/upload-folder', {
                    method: 'POST',
                    body: formData,
                });
                const result = await response.json();
                displayBagId(result.bag_id);
            } catch (error) {
                alert('Error uploading folder');
            }
        }
    });

function displayBagId(bagId) {
    const bagIdContainer = document.getElementById('bagIdContainer');
    const bagIdElement = document.getElementById('bagId');

    bagIdElement.textContent = bagId;
    bagIdContainer.style.display = 'block';

    bagIdElement.addEventListener('click', () => {
        if (navigator.clipboard) {
            navigator.clipboard
                .writeText(bagId)
                .then(() => {
                    alert('BagID copied to clipboard');
                })
                .catch((err) => {
                    alert('Failed to copy BagID');
                });
        } else {
            alert('Clipboard API not supported');
        }
    });
}
