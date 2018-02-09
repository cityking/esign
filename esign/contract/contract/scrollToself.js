/**
	* 平滑滚动到指定位置
	* @param : target string||object
	* @example : $.scrollTo($('#desID'));
	* 	     $.scrollTo('300px');
	* 	     $scrollTo('300px');
	* @version 1.0
	* @date 2015-10-19 15:09:57
	* @author YJC
	* @github https://github.com/52fhy/scrollTo
	*/
; (function (window) {
  'use strict'
  var scrollTo
  var timer = null
  var scrollTop = 0
  var destOffsetTop = 0
  
  scrollTo = function (target, time) {
    if (typeof target === 'string' || typeof target === 'number') {
      destOffsetTop = parseInt(target)
    } else if (typeof target.offset === 'function') {
      var destOffsetTopObj = target.offset()
      destOffsetTop = destOffsetTopObj.top
    } else {
      throw 'param target error!'
    }

    var startPosY = document.documentElement.scrollTop || document.body.scrollTop
    var distance = destOffsetTop - startPosY
    distance = distance > 0 ? Math.ceil(distance) : Math.floor(distance)
    var cellDistance = distance / (time / 20)
    var i = 0
    var now = null
    timer = setInterval(function () {
      now = document.documentElement.scrollTop || document.body.scrollTop
      i++
      if (i == time / 20) {
        clearInterval(timer)
      }
      window.scrollBy(0, cellDistance)
    }, 20)
  }

  window.scrollTo = scrollTo // 支持$scrollTo('300px');纯js用法
})(window)

