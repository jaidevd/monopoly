function start_game(e) {
  e.preventDefault()
  let p1 = $('#player1name').val()
  if (!p1) {
    p1 = $('#player1name').attr('placeholder')
  }
  let p2 = $('#player2name').val()
  if (!p2) {
    p2 = $('#player2name').attr('placeholder')
  }
  $('#p1name').text(p1)
  $('#p2name').text(p2)
  $.post('playerinit', {p1: p1, p2: p2}, (e) => {
    $('.modal').modal('toggle')
    players.push(p1, p2)
    pick_starter()
    updateBalance()
  })
}

function roll() {
  return Math.ceil(Math.random() * 6)
}

function pick_starter() {
  let rolls = []
  let msg = ""
  for (let index = 0; index < players.length; index++) {
    let pl = players[index]
    let myroll = roll() + roll()
    msg += `</p>${pl} rolled ${myroll}.</p>`
    rolls.push({'name': pl, 'rolls': myroll})
  }
  let winner = _.orderBy(rolls, 'rolls').pop().name
  msg += `<p>${winner} plays first.</p>`
  currentPlayer = winner
  enableDisableTurns()
  $('#log').html(msg)
}

function play() {
  $.get('play', {'p1': currentPlayer}, (e) => {
    $('#log').html(e)
    let card = $('.card')
    card.scrollTop(card.prop('scrollHeight'))
    pick_next_player()
    updateBalance()
  })
}


function pick_next_player() {
  $.post('nextplayer', {'player': currentPlayer}, (e) => {
    currentPlayer = e
    enableDisableTurns()
  })
}

function updateBalance() {
  for (let index = 0; index < players.length; index++) {
    let pl = players[index]
    let id = index + 1
    $.get(`balance/${pl}`, (e) => {
      let balance = parseInt(e)
      let sign = ""
      if (balance > 0) {
        sign = "success"
      } else if (balance < 0) {
        sign = "danger"
      } else {
        sign = "warning"
      }
      $(`#p${id}balance`).html(`<span class="text-${sign}">${balance}</span>`)
    })
  }
}

function enableDisableTurns() {
  for (let index = 0; index < players.length; index++) {
    let pl = players[index]
    let id = index + 1
    if (pl == currentPlayer) {
      $(`#p${id}roll`).prop('disabled', false)
      $(`#p${id}roll`).prop('enabled', true)
    } else {
      $(`#p${id}roll`).prop('disabled', true)
      $(`#p${id}roll`).prop('enabled', false)
    }
  }
}
