const videoPlayer = document.querySelector('.video-player')
const video = videoPlayer.querySelector('.video')
const playButton = videoPlayer.querySelector('.play-button')
const volume = videoPlayer.querySelector('.volume')
const currentTimeElement = videoPlayer.querySelector('.current')
const durationTimeElement = videoPlayer.querySelector('.duration')
const progress = videoPlayer.querySelector('.video-progress')
const progressBar = videoPlayer.querySelector('.video-progress-filled')
let array_input = []

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

function myFunc(vars) {
    array_input = vars
}

//Progress bar
video.addEventListener('timeupdate', () =>{

  let tme = array_input
  let current = 0
  let flag = true
  while(flag && array_input.length !== 0){
    let element = tme[current]
    if(video.currentTime > element[1] && video.currentTime <= element[2] ) {
      if(element[0] === 'female'){
        progressBar.style.background = 'red'
      }
      else if(element[0] === 'male'){
        progressBar.style.background = 'blue'
      }
      else if(element[0] === 'music'){
        progressBar.style.background = 'green'
      }
      else {
        progressBar.style.background = 'yellow'
      }
      let percentage = (video.currentTime / video.duration) * 100
      progressBar.style.width = `${percentage}%`
    }
    if((current +1) < tme.length ){
        current += 1
    }
    else{
      flag = false
    }
  }

})

//change progress bar on click
progress.addEventListener('click', (e) =>{
  const progressTime = (e.offsetX / progress.offsetWidth) * video.duration
  video.currentTime = progressTime
})
