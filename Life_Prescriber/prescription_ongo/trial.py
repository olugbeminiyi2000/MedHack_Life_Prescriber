

# Create an email connection
connection = mail.get_connection()

# Manually open the connection
connection.open()

# Initialize an empty list to store email messages
list_of_mail = []

for prescription_object in all_prescription_objects:
    # Construct the HTML content for the email
    html_content = f"""
        <div>
            <div>
                <p>This is a reminder from the hospital for you to take your medication at {prescription_object.first_time}.</p>
                <p>More details concerning your medication:</p>
            </div>
            <div>
                <ul>
                    <li>Total Tablets: {prescription_object.total_tablets}</li>
                    <li>Number of times per day: {prescription_object.no_of_times_per_day}</li>
                    <li>Number of tablets to take: {prescription_object.no_of_tablets_per_use}</li>
                </ul>
            </div>
            <div>
                General Description: {prescription_object.general_description}
            </div>
            <div>
                <p>Click link if prescribed drug has ben used <a href="" target="_blank">Drug Used</a></p>
            </div>
        </div>
    """

    # Create an EmailMessage with the HTML content
    email = mail.EmailMessage(
        subject="Prescription Reminder",
        body=html_content,
        from_email="obolo.emmanuel31052000@gmail.com",
        to=[prescription_object.prescribed_user.email],
        connection=connection,  # Use the existing connection
    )

    # Set the content subtype to HTML
    email.content_subtype = "html"

    # Append the email to the list
    list_of_mail.append(email)

# Send all emails in a single call
connection.send_messages(list_of_mail)

# Close the connection
connection.close()
