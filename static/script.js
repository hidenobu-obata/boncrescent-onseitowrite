async function uploadFile() {
    const fileInput = document.getElementById('audioFile');
    const messageDiv = document.getElementById('message');
    const resultArea = document.getElementById('result');
    
    if (fileInput.files.length === 0) {
        messageDiv.innerText = "ファイルを選択してください";
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    try {
        const response = await fetch('/upload', { method: 'POST', body: formData });
        const data = await response.json();
        
        if (!response.ok) {
            messageDiv.innerText = data.error;
        } else {
            resultArea.value = data.text;
            messageDiv.innerText = "";
        }
    } catch (e) {
        messageDiv.innerText = "システムエラー";
    }
}