async function send_to_server(btn_type) {
  try {
      // Get form fields
      const name = document.getElementById('name').value;
      const fav_player = document.getElementById('fav_player').value;
      const about_me = document.getElementById('about_me').value;
      const vk_acc = document.getElementById('vk_acc').value;
      const telegram_acc = document.getElementById('telegram_acc').value;
      const profile_pic = document.getElementById('profile_pic').files[0];

      // Use FormData to handle both file and JSON data
      const formData = new FormData();
      formData.append('btn_type', btn_type);
      formData.append('name', name);
      formData.append('fav_player', fav_player);
      formData.append('about_me', about_me);
      formData.append('vk_acc', vk_acc);
      formData.append('telegram_acc', telegram_acc);

      // Add the profile pic if selected
      if (profile_pic) {
          formData.append('profile_pic', profile_pic);
      }

      // Send the POST request
      const response = await fetch(window.location.href, {
          method: 'POST',
          body: formData // Send as FormData
      });

      const result = await response.json(); // Parse the response
      console.log(result);
      alert(result['change_data'])
      window.location.href = '/account'
      
  } catch (error) {
      console.error('Error: ', error);
      alert(error)
  }
}
