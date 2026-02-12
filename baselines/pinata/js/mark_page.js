// --- 顶部控制块，确保只执行一次 ---
if (!window._pinataCustomCssAndLabelsInjected) { // 使用一个新的全局变量作为标志，涵盖样式和labels
    const customCSS = `
        ::-webkit-scrollbar {
            width: 10px;
        }
        ::-webkit-scrollbar-track {
            background: #27272a;
        }
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 0.375rem;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
    `;

    const styleTag = document.createElement("style");
    styleTag.textContent = customCSS;
    document.head.append(styleTag);

    window.labels = []; // 将 labels 声明为全局变量，并确保只声明一次
    // 在这个顶层作用域声明的函数也会被保留，因为它们是在全局作用域定义的
    window.unmarkPage = function() {
        // Unmark page logic
        for (const label of window.labels) { // 使用 window.labels
            document.body.removeChild(label);
        }
        window.labels = []; // 重置时也要使用 window.labels
        document.querySelectorAll("[data-mark]").forEach((element) => {
            element.removeAttribute("data-mark");
        });
    };

    window._pinataCustomCssAndLabelsInjected = true; // 设置标志
}
// --- 顶部控制块结束 ---

// markPage 函数本身需要能够在每次调用时重置或更新，所以它不应该被一次性注入
// 它的定义应该在全局变量 _pinataCustomCssAndLabelsInjected 检查之外
// 确保 markPage 每次都能重新获取并标记元素
function markPage() {
  window.unmarkPage(); // 调用全局的 unmarkPage

  // var bodyRect = document.body.getBoundingClientRect(); // 这行是注释掉的，无需改动

  var items = Array.prototype.slice
    .call(document.querySelectorAll("*"))
    .map(function (element) {
      var vw = Math.max(
        document.documentElement.clientWidth || 0,
        window.innerWidth || 0,
      );
      var vh = Math.max(
        document.documentElement.clientHeight || 0,
        window.innerHeight || 0,
      );
      var textualContent = element.textContent.trim().replace(/\s{2,}/g, " ");
      var elementType = element.tagName.toLowerCase();
      var ariaLabel = element.getAttribute("aria-label") || "";

      var rects = [...element.getClientRects()]
        .filter((bb) => {
          var center_x = bb.left + bb.width / 2;
          var center_y = bb.top + bb.height / 2;
          var elAtCenter = document.elementFromPoint(center_x, center_y);

          return elAtCenter === element || element.contains(elAtCenter);
        })
        .map((bb) => {
          const rect = {
            left: Math.max(0, bb.left),
            top: Math.max(0, bb.top),
            right: Math.min(vw, bb.right),
            bottom: Math.min(vh, bb.bottom),
          };
          return {
            ...rect,
            width: rect.right - rect.left,
            height: rect.bottom - rect.top,
          };
        });

      var area = rects.reduce((acc, rect) => acc + rect.width * rect.height, 0);

      return {
        element: element,
        include:
          element.tagName === "INPUT" ||
          element.tagName === "TEXTAREA" ||
          element.tagName === "SELECT" ||
          element.tagName === "BUTTON" ||
          element.tagName === "A" ||
          element.onclick != null ||
          window.getComputedStyle(element).cursor == "pointer" ||
          element.tagName === "IFRAME" ||
          element.tagName === "VIDEO",
        area,
        rects,
        text: textualContent,
        type: elementType,
        ariaLabel: ariaLabel,
      };
    })
    .filter((item) => item.include && item.area >= 20);

  // Only keep inner clickable items
  items = items.filter(
    (x) => !items.some((y) => x.element.contains(y.element) && !(x == y)),
  );

  // Function to generate random colors (这个函数可以放在内部，或者如果它也是全局复用的，也可以移到上面)
  function getRandomColor() {
    var letters = "0123456789ABCDEF";
    var color = "#";
    for (var i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }

  // Lets create a floating border on top of these elements that will always be visible
  items.forEach(function (item, index) {
    item.rects.forEach((bbox) => {
      newElement = document.createElement("div"); // 这里没有用 let/const，会自动变成全局变量，但因为每次markPage都会创建新的div，所以通常不是问题
      var borderColor = getRandomColor();
      newElement.style.outline = `2px dashed ${borderColor}`;
      newElement.style.position = "fixed";
      newElement.style.left = bbox.left + "px";
      newElement.style.top = bbox.top + "px";
      newElement.style.width = bbox.width + "px";
      newElement.style.height = bbox.height + "px";
      newElement.style.pointerEvents = "none";
      newElement.style.boxSizing = "border-box";
      newElement.style.zIndex = 2147483647;
      // newElement.style.background = `${borderColor}80`;

      // Add floating label at the corner
      var label = document.createElement("span");
      label.textContent = index;
      label.style.position = "absolute";
      // These we can tweak if we want
      label.style.top = "-19px";
      label.style.left = "0px";
      label.style.background = borderColor;
      // label.style.background = "black";
      label.style.color = "white";
      label.style.padding = "2px 4px";
      label.style.fontSize = "12px";
      label.style.borderRadius = "2px";
      newElement.appendChild(label);

      document.body.appendChild(newElement);
      window.labels.push(newElement); // 注意这里，改为 window.labels
      // item.element.setAttribute("-ai-label", label.textContent);
    });
    item.element.setAttribute("data-mark", `${index}`);
  });
  const coordinates = items.flatMap((item) =>
    item.rects.map(({ left, top, width, height }) => ({
      x: (left + left + width) / 2,
      y: (top + top + height) / 2,
      type: item.type,
      text: item.text,
      ariaLabel: item.ariaLabel,
    })),
  );
  return coordinates;
}

window.markPage = markPage; // 这行保持不变，确保 markPage 函数被正确挂载到全局 window 对象上