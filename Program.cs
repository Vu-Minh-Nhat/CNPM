
using Microsoft.EntityFrameworkCore;
using ARIMMS.Api.Data;

var builder = WebApplication.CreateBuilder(args);

// Register OpenAPI
builder.Services.AddOpenApi();

// Register PostgreSQL database
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(
        builder.Configuration.GetConnectionString("DefaultConnection")
    ));

var app = builder.Build();

// Configure OpenAPI for development
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

app.UseHttpsRedirection();
app.MapGet("/", () => Results.Ok(new
{
    application = "AR-IMMS API",
    status = "Running"
}));
app.Run();
