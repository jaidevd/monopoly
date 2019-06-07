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
    updateAssets()
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
  $('#log').html(msg)
}

function play() {
  let assets = playerAssets[currentPlayer]
  let cgroup = ""
  if (assets.colorgroups.length > 0) {
    $.get(`developable/${currentPlayer}`, (e) => {
      cgroup = e
      let to_develop = confirm(`${currentPlayer}, you can develop the ${cgroup} colorgroup. Proceed?`)
      if (to_develop) {
        $.get(`build/${cgroup}`)
      }
    })
  }
  $.get('play', {'p1': currentPlayer}, (e) => {
    $('#log').html(e)
    let card = $('#logcard')
    card.scrollTop(card.prop('scrollHeight'))
    pick_next_player()
    updateAssets()
  })
}


function pick_next_player() {
  $.post('nextplayer', {'player': currentPlayer}, (e) => {
    currentPlayer = e
  })
}

function updateAssets() {
  for (let index = 0; index < players.length; index++) {
    let pl = players[index]
    let id = index + 1
    drawStatusCard(pl, id)
  }
}

function drawStatusCard(player, id) {
  let bdiv = $(`#p${id}balance`)
  let pdiv = $(`#p${id}properties`)
  $.getJSON(`wealth/${player}`, (e) => {
    playerAssets[player] = e

    let bcol = ""
    if (e.balance < 0) {
      bcol = "danger"
    } else if (e.balance == 0) {
      bcol = "warning"
    } else {
      bcol = "success"
    }
    bdiv.html(`<span class="text-${bcol}">${e.balance}</span>`)

    let html = ""
    if (e.in_jail) {
      html += `<p><span class="text-danger">${player} is in Jail!</span></p>`
    }
    html += "<p>Properties Owned:</p><ul>"
    for (let index=0; index < e.properties.length; index++) {
      let property = e.properties[index]
      if (property.is_mortgaged) {
        html += `<li>${property.name} <span class="badge badge-danger">Mortgaged<span></li>`
      } else {
        html += `<li>${property.name}</li>`
      }
    }
    html += "</ul>"
    html += "<p>Colorgroups:</p><ul>"
    for (let index=0; index < e.colorgroups.length; index++) {
      let cg = e.colorgroups[index]
      html += `<li>${cg}</li>`
    }
    html += "</ul>"
    pdiv.html(html)
  })
}
