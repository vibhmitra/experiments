const files = ['./apiresponse.json']; // Add your file paths here

Promise.all(files.map(file => fetch(file).then(response => response.json())))
  .then(allData => {
    const tableBody = document.getElementById('subscriptionsTable').getElementsByTagName('tbody')[0];
    let serialNumber = 1; // Initialize serial number

    allData.forEach(data => {
      data.items.forEach(subscription => {
        // Creating Row and Data
        const row = document.createElement('tr');
        const serialNumberCell = document.createElement('td');
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
        // adding serial number
        serialNumberCell.textContent = serialNumber++;
        
        // adding image data
        const imagebox = document.createElement('img');
        imagebox.setAttribute('src', subscription.snippet.thumbnails.high.url);
        imagebox.style.maxWidth = '100px';
        imageCell.appendChild(imagebox);
        
        // Creating Links
        const link = document.createElement('a');
        link.setAttribute('href', 'https://www.youtube.com/channel/' + subscription.snippet.resourceId.channelId);
        link.textContent = subscription.snippet.title;
        channelTitleCell.appendChild(link);
        
        // adding date
        let publishdate = new Date(subscription.snippet.publishedAt);
        publishedAtCell.textContent = formatDate(publishdate);
        
        // adding description
        channelDescriptionCell.textContent = subscription.snippet.description;
        
        row.appendChild(serialNumberCell);
        row.appendChild(publishedAtCell);
        row.appendChild(imageCell);
        row.appendChild(channelTitleCell);
        row.appendChild(channelDescriptionCell);
        tableBody.appendChild(row);
      });
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
