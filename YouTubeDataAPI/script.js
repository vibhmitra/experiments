
fetch('./part2.txt') // Replace 'subscriptions.json' with your file path
  .then(response => response.json())
  .then(data => {
    const tableBody = document.getElementById('subscriptionsTable').getElementsByTagName('tbody')[0];
    data.items.forEach(subscription => {
      // Creating Row and Data
      const row = document.createElement('tr');
      const publishedAtCell = document.createElement('td');
      const channelTitleCell = document.createElement('td');
      const channelDescriptionCell = document.createElement('td');
      const imageCell = document.createElement('td');
      

      // Styling
      publishedAtCell.style.whiteSpace = 'nowrap';
      channelTitleCell.style.whiteSpace = 'nowrap';
      channelDescriptionCell.style.wordWrap = 'break-word';
      channelDescriptionCell.style.overflow = 'hidden';
      channelDescriptionCell.style.textOverflow = 'ellipsis';

      // Inserting Data

      // adding image data
      const imagebox = document.createElement('img');
      imagebox.setAttribute('src', subscription.snippet.thumbnails.default.url);
      imageCell.appendChild(imagebox);
      
      // Creating Links
      // Create the anchor (link) element
      const link = document.createElement('a');
      // Set the attributes for the anchor element
      link.setAttribute('href', 'https://www.youtube.com/channel/'+(subscription.snippet.resourceId.channelId)); // Replace with your URL
      link.textContent = subscription.snippet.title; // Replace with your link text
      // Append the anchor element to the table cell
      channelTitleCell.appendChild(link);
      
      // adding date
      let publishdate = new Date(subscription.snippet.publishedAt);
      publishedAtCell.textContent = formatDate(publishdate);
      
      // adding description
      channelDescriptionCell.textContent = subscription.snippet.description;
      
      row.appendChild(publishedAtCell);
      row.appendChild(imageCell);
      row.appendChild(channelTitleCell);
      row.appendChild(channelDescriptionCell);
      tableBody.appendChild(row);
    });
  })
  .catch(error => console.error('Error:', error));

  // Function to convert Date
  function formatDate(date) {
    const pad = (num) => (num < 10 ? '0' : '') + num;

    const year = date.getFullYear();
    const month = pad(date.getMonth() + 1);
    const day = pad(date.getDate());
    const hours = pad(date.getHours());
    const minutes = pad(date.getMinutes());
    const timeZoneOffset = -date.getTimezoneOffset();
    const sign = timeZoneOffset >= 0 ? '+' : '-';
    const offsetHours = pad(Math.floor(Math.abs(timeZoneOffset) / 60));
    const offsetMinutes = pad(Math.abs(timeZoneOffset) % 60);

    return `${year}-${month}-${day} ${hours}:${minutes} ${sign}${offsetHours}:${offsetMinutes}`;
}

