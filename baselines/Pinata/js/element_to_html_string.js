function elementToHtmlString(element) {
  const attributes = Array.from(element.attributes)
    .map((attr) =>
      ["data-mark"].includes(attr.name) ? "" : `${attr.name}="${attr.value}"`,
    )
    .join(" ");
  if (element.tagName.toLowerCase() === "select") {
    const options = Array.from(element.children)
      .filter((child) => child.tagName.toLowerCase() === "option")
      .map((option) => {
        const value = option.getAttribute("value")?.trim() ?? "";
        const innerText = option.textContent?.trim() ?? "";
        if (innerText === "") return value;
        return innerText;
      })
      .join(", ");
    return `<${element.tagName.toLowerCase()} ${attributes}>${options}</${element.tagName.toLowerCase()}>`;
  }
  const innerText = element.textContent?.trim();
  return (
    `<${element.tagName.toLowerCase()} ${attributes}>` +
    innerText +
    `</${element.tagName.toLowerCase()}>`
  );
}

window.elementToHtmlString = elementToHtmlString;
