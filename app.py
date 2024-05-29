import aws_cdk
from newton.stack import NewtonStack

app = aws_cdk.App()
NewtonStack(app, "newton")

app.synth()
