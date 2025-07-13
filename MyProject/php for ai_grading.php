<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $file = $_FILES['project']['tmp_name'];
    $code = file_get_contents($file);

    $data = http_build_query([
        'title' => $_POST['title'],
        'code' => $code
    ]);

    $options = [
        'http' => [
            'header'  => "Content-type: application/x-www-form-urlencoded",
            'method'  => 'POST',
            'content' => $data,
        ],
    ];

    $context  = stream_context_create($options);
    $result = file_get_contents('http://127.0.0.1:8000/api/grade-project/', false, $context);
    $response = json_decode($result, true);

    echo "<h2>AI Grading Result</h2>";
    if (isset($response['error'])) {
        echo "<p style='color:red;'>Error: " . htmlspecialchars($response['error']) . "</p>";
    } else {
        echo "<p><strong>Grade:</strong> " . htmlspecialchars($response['grade']) . "</p>";
        echo "<p><strong>Feedback:</strong> " . nl2br(htmlspecialchars($response['feedback'])) . "</p>";
    }
}
?>

<!-- HTML Upload Form -->
<form method="POST" enctype="multipart/form-data">
    <label>Project Title:</label><br>
    <input type="text" name="title" required><br><br>

    <label>Upload  Project:</label><br>
    <input type="file" name="project" required><br><br>

    <button type="submit">Submit Project</button>
</form>
