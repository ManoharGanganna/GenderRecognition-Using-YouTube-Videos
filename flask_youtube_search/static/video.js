const videoPlayer = document.querySelector('.video-player')
const video = videoPlayer.querySelector('.video')
const playButton = videoPlayer.querySelector('.play-button')
const volume = videoPlayer.querySelector('.volume')
const currentTimeElement = videoPlayer.querySelector('.current')
const durationTimeElement = videoPlayer.querySelector('.duration')
const progress = videoPlayer.querySelector('.video-progress')
const progressBar = videoPlayer.querySelector('.video-progress-filled')


//Play and Pause button
playButton.addEventListener('click', (e) => {
  if(video.paused){
    video.play()
    e.target.textContent = '❚ ❚'
  } else {
    video.pause()
    e.target.textContent = '►'
  }
})

//volume
volume.addEventListener('mousemove', (e)=> {
  video.volume = e.target.value
})

//current time and duration
const currentTime = () => {
  let currentMinutes = Math.floor(video.currentTime / 60)
  let currentSeconds = Math.floor(video.currentTime - currentMinutes * 60)
  let durationMinutes = Math.floor(video.duration / 60)
  let durationSeconds = Math.floor(video.duration - durationMinutes * 60)

  currentTimeElement.innerHTML = `${currentMinutes}:${currentSeconds < 10 ? '0'+currentSeconds : currentSeconds}`
  durationTimeElement.innerHTML = `${durationMinutes}:${durationSeconds}`
}

video.addEventListener('timeupdate', currentTime)


//Progress bar
video.addEventListener('timeupdate', () =>{
  const percentage = (video.currentTime / video.duration) * 100
  //const arr = [['music', 0, 8], ['female', 8, 12], ['male', 12, 66], ['music', 66, 70], ['noEnergy', 70, 100]]
  progressBar.style.width = `${percentage}%`

  // for (let i = 0; i < arr.length; i++) {
  //     console.log('arr', arr[i])
  //     for (let j = 0; j < arr[i].length; j++) {
  //       console.log('type', arr[i][0])
  //       console.log('percentage', arr[i][2])
  //       let color = "";
  //       switch (arr[i][0]) {
  //         case "music":
  //           color = "red";
  //           break;
  //         case "male":
  //           color = "blue";
  //           break;
  //         case "female":
  //           color = "yellow";
  //           break;
  //         color = "green";
  //           break;
  //       }
  //
  //       if(percentage < arr[i][2]) {
  //         progressBar.style.width = `${percentage}%`;
  //          console.log('col',color)
  //         progressBar.style.background = color;
  //       }
  //     }
  //
  //   }
  // //progressBar.style.background ='linear-gradient(to right,red 20%, orange 20% 40%, yellow 40% 60%, green 60% 80%, blue 80%)';
  // if (percentage < 40){
  //   progressBar.style.width = `${percentage}%`
  //   progressBar.style.background = 'green'
  // }
  // else{
  //   progressBar.style.width = `${percentage}%`
  //   progressBar.style.background = 'yellow'
  // }
  // setTimeout(()=>{
  //   progressBar.style.background ='linear-gradient(to right,red 20%, orange 20% 40%, yellow 40% 60%, green 60% 80%, blue 80%)';
  // },video.duration)

})

//change progress bar on click
progress.addEventListener('click', (e) =>{
  const progressTime = (e.offsetX / progress.offsetWidth) * video.duration
  video.currentTime = progressTime
})