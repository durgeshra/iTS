// Generated by CoffeeScript 1.9.3
var add, create_scope_groups, define_variable, delete_scope_groups, update_variable;

define_variable = function(type, scp, name, val, id) {
  var scope, variable;
  scope = $('#' + scp);
  scope.append('<div id=\'' + id + '\'></div>');
  variable = $('#' + id);
  variable.append('<div class=\'tagTop\'></div>');
  variable.append('<div class=\'tagBot\'></div>');
  variable.children('.tagBot').html(val);
  variable.children('.tagTop').append('<div class="name"></div>');
  variable.children('.tagTop').append('<div class="type"></div>');
  variable.children('.tagTop').children('.name').html(name);
  variable.children('.tagTop').children('.type').html(type);
  variable.addClass('newborn');
  return setTimeout((function() {
    return variable.addClass('var').removeClass('newborn');
  }), 10);
};

update_variable = function(id, val) {
  var variable;
  variable = $('#' + id);
  return variable.children('.tagBot').html(val);
};

create_scope_groups = function(scp, id) {
  var a, h, h2, i, j, l, max, ref;
  l = $('.var').length;
  max = 0;
  for (i = j = 0, ref = l - 1; 0 <= ref ? j <= ref : j >= ref; i = 0 <= ref ? ++j : --j) {
    a = $('#' + scp + ' .var')[i];
    h = parseInt($(a).css('margin-bottom')) + parseInt($(a).css('height')) + parseInt($(a).css('margin-top')) + parseInt($(a).css('top')) + 30;
    console.log($(a).css('margin-bottom'));
    if (h > max) {
      max = h;
    }
  }
  h2 = parseInt($('#' + scp).css('height')) - max;
  $('#' + scp).append('<div id="' + id + '"></div>');
  $('#' + id).css('width', '100%');
  $('#' + id).css('height', h2 + 'px');
  $('#' + id).css('border', 'solid 1px black');
  $('#' + id).css('border-radius', '2%');
  $('#' + id).css('display', 'flex');
  $('#' + id).css('flex-wrap', 'wrap');
  return $('#' + id).css('margin', '5px');
};

delete_scope_groups = function(id) {
  return $('#' + id).remove();
};

$(function() {
  return define_variable('int', 'global', 'a', 32, 'global_a');
});

$(function() {
  return define_variable('int', 'global', 'b', 32, 'global_b');
});

$(function() {
  return update_variable('global_a', 69);
});

$(function() {
  return setTimeout((function() {
    return create_scope_groups('global', 'global_15');
  }), 1000);
});

add = function() {
  return define_variable($('#getT').val(), $('#getS').val(), $('#getN').val(), $('#getV').val(), $('#getI').val());
};