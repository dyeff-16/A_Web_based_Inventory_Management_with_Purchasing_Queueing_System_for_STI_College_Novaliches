import turtle

screen = turtle.Screen()
screen.title("Pagong Race")
screen.bgcolor("Green")
t1 = turtle.Turtle()
t2 = turtle.Turtle()

finish_line = 200
line = turtle.Turtle()
line.penup()
line.goto(finish_line, 100)
line.pensize(3)
line.pendown()
line.right(90)
line.forward(200)
line.hideturtle()

t1.color("Pink")
t2.color("blue")
t1.shape("turtle")
t2.shape("turtle")

t1.penup()
t1.goto(-200, 50)
t2.penup()
t2.goto(-200, -50)

def t1_forward():
    if t1.xcor() < finish_line:
        t1.forward(5)
        check_winner()

def t2_forward():
    if t2.xcor() < finish_line:
        t2.forward(5)
        check_winner()

def check_winner():
    if t1.xcor() >= finish_line:
        announce_winner("Pink")
    elif t2.xcor() >= finish_line:
        announce_winner("Blue")

def announce_winner(winner):
    winner_text = turtle.Turtle()
    winner_text.hideturtle()
    winner_text.penup()
    winner_text.goto(0, 0)
    winner_text.write(f"{winner} Turtle Wins!", align="center")
    screen.update()

screen.listen()
screen.onkey(t1_forward, "w")
screen.onkey(t2_forward, "Up")


screen.mainloop()
