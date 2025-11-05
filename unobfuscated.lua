pcall(function()
    game.StarterGui:SetCore("SendNotification", {
        Title = "Hello!";
        Text = "This is a test notification.";
        Duration = 3;
    })
end)
