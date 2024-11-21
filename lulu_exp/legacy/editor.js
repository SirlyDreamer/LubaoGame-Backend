let cardGroup;
let deletedCards = []; // 用于存储删除的卡片，以支持撤销删除
let unpositionedCardCount = 0;
let ifGenerating = false;
let mascot;
let mascotImg;
let answerText = "";
let cardCount = 0; // 用于生成卡片序号
let selectedCard = null; 
let lastMousePressed = false;
let inputBox; // 实际上是显示的文字
let uiContainer;

let UIratio = 0.3;
let canvasWidth;


let clickTextBox;

let errorTextBox;
let correctTextBox;
let backPathTextBox;

let candSelectBox;
let movableSelectBox;

let checkGridSnapping;

let enableGridSnapping = true;

let gripSnappingSize = 5;

let canvasScale = 1;

let backgroundImg; // Variable to hold the loaded background image

let canvasHeight;

function preload() {
  mascotImg = loadImage("images/mascot.png");
}

function drawSprites() {}

function setup() {
  canvasWidth = windowWidth * (1 - UIratio); // 左侧 70%
  
  windowHeight = canvasWidth * 600 / 800;
  canvasHeight = windowHeight;

  canvasScale = canvasWidth / 800;

  gripSnappingSize = windowHeight / 60;

  createCanvas(canvasWidth, windowHeight);
  // createPromptInput();

  cardGroup = new Group();

  mascot = createSprite(width / 8, 100, 100, 100);
  mascot.addImage(mascotImg);
  mascot.scale = 1;
  mascot.rotation = 180;
  mascot.collider = "none";

  // 创建右侧 30% 的 UI 控制区域
  uiContainer = createDiv();
  uiContainer.size(windowWidth * 0.3, windowHeight);
  uiContainer.position(windowWidth * 0.7, 0);
  uiContainer.style("background-color", "#f4f4f4");

  createEditorButtons();
}

function loadBackgroundImage(){

}


function loadSolution(){
  
}


function createEditorButtons() {
  let heightOffset = max(windowHeight * 0.06, 50);
  let nLine = 0;

  // print heightOffset in console!
  console.log("heightOffset: " + heightOffset);


  let addButton = createButton("增加卡片").parent(uiContainer);
  addButton.style("font-size", "36px");
  addButton.mousePressed(() => addCard(false));

  let addTargetButton = createButton("添加 target").parent(uiContainer).position(windowWidth*0.1, nLine * heightOffset);
  addTargetButton.style("font-size", "36px");
  addTargetButton.mousePressed(() => addCard(true));

  nLine += 1;

  // 在下面一行 设置删除和撤销删除
  let deleteButton = createButton("删除对象").parent(uiContainer).position(0, nLine * heightOffset);
  // let deleteButton = createButton("删除对象").position(170 * 3, height - 10);
  deleteButton.style("font-size", "36px");
  deleteButton.mousePressed(deleteSelectedCard); // 绑定删除功能

  let undoButton = createButton("撤销删除").parent(uiContainer).position(windowWidth*0.1, nLine * heightOffset);
  undoButton.style("font-size", "36px");
  undoButton.mousePressed(undoDelete); // 绑定撤销删除功能

  nLine += 1;

  inputBox = createInput().parent(uiContainer).position(0, nLine * heightOffset);
  // inputBox.position(10, height + 50);
  inputBox.style("font-size", "36px");
  inputBox.size(200);

  let modifyButton = createButton("修改文字").parent(uiContainer).position(windowWidth*0.1, nLine * heightOffset);
  // modifyButton.position(inputBox.x + inputBox.width + 10, height + 50);
  modifyButton.style("font-size", "36px");
  modifyButton.mousePressed(modifySelectedCardText); // 绑定修改文字功能

  nLine += 1;

  // TextBox and Button for "修改ClickText"
  clickTextBox = createInput().parent(uiContainer).position(0, nLine * heightOffset);
  clickTextBox.style("font-size", "36px");
  clickTextBox.size(200);

  let modifyClickTextButton = createButton("修改ClickText").parent(uiContainer).position(windowWidth * 0.1, nLine * heightOffset);
  modifyClickTextButton.style("font-size", "36px");
  modifyClickTextButton.mousePressed(() => modifyClickText(clickTextBox.value()));

  nLine += 1;

  // TextBox and Button for "修改ErrorText"
  errorTextBox = createInput().parent(uiContainer).position(0, nLine * heightOffset);
  errorTextBox.style("font-size", "36px");
  errorTextBox.size(200);

  let modifyErrorTextButton = createButton("修改ErrorText").parent(uiContainer).position(windowWidth * 0.1, nLine * heightOffset);
  modifyErrorTextButton.style("font-size", "36px");
  modifyErrorTextButton.mousePressed(() => modifyErrorText(errorTextBox.value()));

  nLine += 1;

  // TextBox and Button for "修改CorrectText"
  correctTextBox = createInput().parent(uiContainer).position(0, nLine * heightOffset);
  correctTextBox.style("font-size", "36px");
  correctTextBox.size(200);

  let modifyCorrectTextButton = createButton("修改CorrectText").parent(uiContainer).position(windowWidth * 0.1, nLine * heightOffset);
  modifyCorrectTextButton.style("font-size", "36px");
  modifyCorrectTextButton.mousePressed(() => modifyCorrectText(correctTextBox.value()));

  nLine += 1;

  // 显示文字 "是否候选卡"
  let candidateText = createP("是否候选卡").parent(uiContainer).position(0, (nLine-0.5) * heightOffset);
  candidateText.style("font-size", "36px");

  // 添加下拉式单选框
  candSelectBox = createSelect().parent(uiContainer).position(windowWidth * 0.1, nLine * heightOffset);
  candSelectBox.style("font-size", "36px");
  candSelectBox.option("auto");
  candSelectBox.option("game");
  candSelectBox.option("candidate");
  candSelectBox.changed(() => {
    if (selectedCard){
      selectedCard.candSelect = candSelectBox.value();
    }
  });

  nLine += 1;

  // 显示文字 "是否可以移动"
  let movableText = createP("可以移动").parent(uiContainer).position(0, (nLine-0.5) * heightOffset);
  movableText.style("font-size", "36px");

  // 添加下拉式单选框
  movableSelectBox = createSelect().parent(uiContainer).position(windowWidth * 0.1, nLine * heightOffset);
  movableSelectBox.style("font-size", "36px");
  movableSelectBox.option("moveable");
  movableSelectBox.option("unmoveable");
  movableSelectBox.changed(() => {
    if (selectedCard){
      selectedCard.movableSelect = movableSelectBox.value();
    }
  })

  nLine += 1;

  let loadBackLabel = createP("载入背景图:").parent(uiContainer).position(0, (nLine-0.5) * heightOffset);
  loadBackLabel.style("font-size", "36px");

  let loadBackInput = createFileInput(handleBackground).parent(uiContainer);
  loadBackInput.position(windowWidth * 0.1, nLine * heightOffset);
  loadBackInput.style("font-size", "36px");



  // backPathTextBox = createInput().parent(uiContainer).position(0, nLine * heightOffset);
  // backPathTextBox.style("font-size", "36px");
  // backPathTextBox.size(200);

  // let loadBackgroundButton = createButton("载入背景图").parent(uiContainer).position(windowWidth * 0.1, nLine * heightOffset);
  // loadBackgroundButton.style("font-size", "36px");
  // loadBackgroundButton.mousePressed(loadBackgroundImage); // Function to load background image

  nLine += 2;

  // 显示文字 文件名:
  let savePathText = createP("文件名:").parent(uiContainer).position(0, (nLine-0.5) * heightOffset);
  savePathText.style("font-size", "36px");

  // Solution save path
  let savePathTextBox = createInput().parent(uiContainer).position(windowWidth * 0.1, nLine * heightOffset);
  savePathTextBox.style("font-size", "36px");
  savePathTextBox.size(200);

  // 保存和载入按钮
  let saveButton = createButton("保存").parent(uiContainer).position(windowWidth * 0.2, nLine * heightOffset);
  saveButton.style("font-size", "36px");
  saveButton.mousePressed(() => saveSolution(savePathTextBox.value() || undefined));

  nLine += 1;
  // 添加载入文件的文本和文件选择器
  let loadButtonLabel = createP("载入文件:").parent(uiContainer).position(0, (nLine-0.5) * heightOffset);
  loadButtonLabel.style("font-size", "36px");

  // 文件选择器用于载入 JSONL 文件
  let loadInput = createFileInput(handleFileLoad).parent(uiContainer);
  loadInput.position(windowWidth * 0.1, nLine * heightOffset);
  loadInput.style("font-size", "36px");

  nLine += 1;

  // 增加网格吸附的文本 和单选框
  let snapText = createP("网格吸附:").parent(uiContainer).position(0, (nLine-0.5) * heightOffset);
  snapText.style("font-size", "36px");

  // 打勾式单选框
  snapCheckbox = createCheckbox('', true).parent(uiContainer).position(windowWidth * 0.1, nLine * heightOffset);
  snapCheckbox.style("font-size", "36px");
  snapCheckbox.style("transform", "scale(2)");

  snapCheckbox.changed(() => {
    enableGridSnapping = snapCheckbox.checked();
  })



  // let loadButton = createButton("载入").parent(uiContainer).position(windowWidth * 0.1, nLine * heightOffset);
  // loadButton.style("font-size", "36px");
  // loadButton.mousePressed(() => loadSolution(savePathTextBox.value() || undefined));

}

function handleBackground(file) {
  if (file.type === 'image') {
    loadImage(file.data, img => {
      backgroundImg = img; // Store the loaded image in the global variable
      console.log("Background image loaded successfully");
    }, err => {
      console.error("Error loading image:", err);
    });
  } else {
    console.log("Unsupported file type. Please upload an image file.");
  }
}


function handleFileLoad(file) {
  if ( file.type === 'text') {
    // cardGroup.removeSprites(); // Clear existing cards

    // clear cardGroup by remove card by card
    while (cardGroup.length > 0) {
      cardGroup[0].remove();
    }

    // Split file data by lines and process each line as JSON
    let lines = file.data.split('\n');
    lines.forEach(line => {
      line = line.trim(); // Remove any extra whitespace
      if (line) {  // Check if line is not empty
        try {
          jsonToCard(line); // Convert JSON string to card
        } catch (error) {
          console.error("Failed to parse line as JSON:", line, error);
        }
      }
    });
    console.log("Loaded layout from uploaded file");
  } else {
    console.log("Unsupported file type. Please upload a JSONL text file.");
  }
}


function draw() {
  clear();
  background(240);

  
  // Draw the background image if it has been loaded
  if (backgroundImg) {
    image(backgroundImg, 0, 0, canvasWidth, canvasHeight * 0.75 );
  } else {
    background(240); // Fallback color if no background image is loaded
  }

  // Draw a horizontal line at 1/6th of the canvas height
  stroke(0);
  line(0, canvasHeight * 0.75, canvasWidth, canvasHeight * 0.75 );


  // 在y = 0.166 * 5.5, x = 0.5 位置 绘制文字"候选卡片区"
  text("候选卡片区", width * 0.5, height * (0.75 + (1-0.75)/2));
  

  if (mouseIsPressed && !lastMousePressed && mouseX <= canvasWidth) {
    for (let card of cardGroup) {
      if (
        mouseX > card.position.x - card.width / 2 &&
        mouseX < card.position.x + card.width / 2 &&
        mouseY > card.position.y - card.height / 2 &&
        mouseY < card.position.y + card.height / 2
      ) {
        if (selectedCard !== card) {
          selectedCard = card; 
          offsetX = mouseX - card.position.x;
          offsetY = mouseY - card.position.y;

          // update clickTextBox value
          inputBox.value(card.text);

          // update  clickText, errorText, correctText value
          correctTextBox.value(card.correctText);
          errorTextBox.value(card.errorText);
          clickTextBox.value(card.clickText);

          candSelectBox.value(card.candSelect);
          movableSelectBox.value(card.movableSelect);

        }
        break;
      } else {
        // if mouse hit in canvas but not in any card, clear selectedCard
        selectedCard = null;
      }
    }
  }

  if (mouseIsPressed && selectedCard && mouseX <= canvasWidth) {
    selectedCard.position.x = mouseX - offsetX;
    selectedCard.position.y = mouseY - offsetY;

    if (enableGridSnapping) {
      selectedCard.position.x = round(selectedCard.position.x / gripSnappingSize) * gripSnappingSize;
      selectedCard.position.y = round(selectedCard.position.y / gripSnappingSize) * gripSnappingSize;
    }
  }

  for (let card of cardGroup) {
    card.rotation = 0;
    card.draw = function() {
      if (card === selectedCard) {
        stroke(0, 255, 0);
        strokeWeight(4);
      } else {
        stroke(0);
        strokeWeight(1);
      }

      if (this.isTarget) {
        fill(220, 240, 255);
        drawingContext.setLineDash([5, 5]);
      } else {
        fill(254, 241, 206);
        drawingContext.setLineDash([]);
      }

      rect(0, 0, this.width, this.height, 10);
      fill(0);
      textAlign(CENTER, CENTER);
      textSize(24);
      text(this.text, 0, 0);
    };
  }

  textSize(24);
  textAlign(LEFT);
  fill(0);
  text(answerText, width * 0.34, height * 0.22);

  lastMousePressed = mouseIsPressed;
  drawSprites();
}



function addCard(isTarget = false) {
  cardCount++;

  card_height = 120

  let x = random(50, width - 50);
  let y = random(150, height - 150);

  cardWidth =  120 * 0.62 * canvasScale;
  cardHeight =  120 * canvasScale;

  let card = createSprite(x, y, cardWidth, cardHeight);
  card.text = isTarget ? "Target"+cardCount.toString() : cardCount.toString();
  card.isTarget = isTarget;

  // 初始化 clickText, errorText, correctText 属性
  card.clickText = "";
  card.errorText = "";
  card.correctText = "";

  // 初始化 candSelect 和 movableSelect 属性
  card.candSelect = "auto";       // 默认值可以设为 auto
  card.movableSelect = isTarget?"unmoveable" : "moveable"; // 默认值可以设为 moveable

  cardGroup.add(card);
}

function cardToJSON(card) {
  return JSON.stringify({
    x: round(card.position.x/canvasScale),
    y: round(card.position.y/canvasScale),
    text: card.text,
    isTarget: card.isTarget,
    clickText: card.clickText,
    errorText: card.errorText,
    correctText: card.correctText,
    candSelect: card.candSelect,
    movableSelect: card.movableSelect
  });
}

function jsonToCard(data) {
  let parsedData = JSON.parse(data);
  let card = createSprite(parsedData.x*canvasScale, parsedData.y*canvasScale, 100, 150);

  card.text = parsedData.text;
  card.isTarget = parsedData.isTarget;
  card.clickText = parsedData.clickText;
  card.errorText = parsedData.errorText;
  card.correctText = parsedData.correctText;
  card.candSelect = parsedData.candSelect;
  card.movableSelect = parsedData.movableSelect;

  cardGroup.add(card);
  return card;
}

function saveSolution(path = undefined) {
  if (!path) {
    let timestamp = new Date().toISOString().replace(/[-:.]/g, ''); // 生成时间戳，去掉无效字符
    path = `temp_${timestamp}.jsonl`;
  }

  let data = cardGroup.map(card => cardToJSON(card)).join('\n'); // 将每个卡片的 JSON 行合并为一个字符串

  // 使用 p5.js 的 saveStrings 函数保存到文件
  saveStrings(data.split('\n'), path); // 将 data 按行分割并保存到文件
  console.log(`Saved to ${path}`);
}

// function saveSolution(path = undefined) {
//   // 如果未定义路径，则使用默认文件名 "temp_时间戳.jsonl"
//   if (!path) {
//     let timestamp = new Date().toISOString().replace(/[-:.]/g, ''); // 生成时间戳，去掉无效字符
//     path = `temp_${timestamp}.jsonl`;
//   }

//   let data = cardGroup.map(card => cardToJSON(card)).join('\n'); // 将每个卡片的 JSON 行合并为一个字符串

//   // 使用 Blob 进行文件下载
//   let blob = new Blob([data], { type: 'text/plain' });
//   let url = URL.createObjectURL(blob);
//   let a = document.createElement('a');
//   a.href = url;
//   a.download = path;
//   a.click();
//   URL.revokeObjectURL(url);
//   console.log(`Saved to ${path}`);
// }




// 删除选中卡片功能
function deleteSelectedCard() {
  if (selectedCard) {
    deletedCards.push(selectedCard); // 将删除的卡片存入删除堆栈
    cardGroup.remove(selectedCard); // 从卡片组中移除
    selectedCard.remove(); // 从画布中移除
    selectedCard = null; // 清除选中的卡片
  }
}

// Undo delete function with sprite recreation
function undoDelete() {
    if (deletedCards.length > 0) {
      let lastDeletedCard = deletedCards.pop(); // Get the last deleted card
  
      // Recreate the sprite with the same properties as the deleted one
      let recreatedCard = createSprite(
        lastDeletedCard.position.x,
        lastDeletedCard.position.y,
        lastDeletedCard.width,
        lastDeletedCard.height
      );
  
      recreatedCard.text = lastDeletedCard.text;
      recreatedCard.isTarget = lastDeletedCard.isTarget;
      cardGroup.add(recreatedCard); // Add the recreated card to the group
  
      // Set additional properties (e.g., draw function) if needed
      recreatedCard.draw = lastDeletedCard.draw;
    }
}
  
// 修改选中文字功能
function modifySelectedCardText() {
  let newText = inputBox.value().trim();
  if (newText && selectedCard) {
    selectedCard.text = newText;
  }
}

function modifyClickText(newText) {
  if (selectedCard && newText.trim()) {
    selectedCard.clickText = newText;
    clickTextBox.value(newText); // 更新显示
  }
}

function modifyErrorText(newText) {
  if (selectedCard && newText.trim()) {
    selectedCard.errorText = newText;
  }
}

function modifyCorrectText(newText) {
  if (selectedCard && newText.trim()) {
    selectedCard.correctText = newText;
  }
}

function createPromptInput() {
  let inputBox = createInput();
  inputBox.style("font-size", "24px");
  inputBox.size(600, 60);
  inputBox.position((width - inputBox.width) / 2, 20);
  inputBox.attribute("wrap", "soft");
  inputBox.style("text-align", "top");
  inputBox.style("background-color", "white");
  inputBox.style("border", "2px solid #ccc");
  inputBox.style("border-radius", "20px");
  inputBox.style("padding", "10px");
  inputBox.style("box-shadow", "0 4px 8px rgba(0,0,0,0.1)");
  inputBox.style("margin", "10px");

  let submitButton = createButton("生成");
  submitButton.position(
    inputBox.x + inputBox.width + 50,
    inputBox.y + inputBox.height / 2 - submitButton.height / 2
  );
  submitButton.style("font-size", "24px");
  submitButton.size(100, 60);
  submitButton.style("background-color", "#007bdd");
  submitButton.style("color", "white");
  submitButton.style("border-radius", "20px");
  submitButton.style("border", "none");
  submitButton.style("padding", "10px 20px");
  submitButton.style("box-shadow", "0 4px 8px rgba(0,0,0,0.1)");
  submitButton.mousePressed(() => {
    let inputText = inputBox.value();
    console.log("Input Text:", inputText);
    cardGroup.amount = 0;
    ifGenerating = true;
    unpositionedCardCount = 0;
    auto_card(inputText);
  });
}

function auto_card(message) {
  // 用于自动生成卡片的函数
}
