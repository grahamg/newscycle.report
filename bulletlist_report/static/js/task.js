function checkTaskStatus(taskId) {
    fetch(`/api/v1/task/${taskId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'complete') {
                console.log('Task completed with result:', data.result);
            } else if (data.status === 'failed') {
                console.log('Task failed:', data.error);
            } else {
                console.log('Task is still running');
            }
        });
}

/* 

Usage Example: Trigger the task and start polling

fetch('/trigger_task/')
    .then(response => response.json())
    .then(data => {
        const taskId = data.task_id;
        checkTaskStatus(taskId);
    });

*/