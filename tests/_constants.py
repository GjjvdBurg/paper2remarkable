# -*- coding: utf-8 -*-

TEST_FILE = (
    "%PDF-1.1\n%¿÷¢þ\n1 0 obj\n<< /Pages 2 0 R /Type /Catalog >>\n"
    "endobj\n2 0 obj\n<< /Count 1 /Kids [ 3 0 R ] /MediaBox [ 0 0 300 600 ] "
    "/Type /Pages >>\nendobj\n3 0 obj\n<< /Contents 4 0 R /Parent 2 0 R "
    "/Resources << /Font << /F1 << /BaseFont /Times-Roman /Subtype /Type1 "
    "/Type /Font >> >> >> /Type /Page >>\nendobj\n4 0 obj\n<< /Length 44 >>\n"
    "stream\nBT /F1 18 Tf 80 80 Td (Hello World 1) Tj ET\nendstream\nendobj\n"
    "xref\n0 5\n0000000000 65535 f \n0000000019 00000 n \n0000000067 00000 n "
    "\n0000000153 00000 n \n0000000306 00000 n \ntrailer << /Root 1 0 R /Size "
    "5 /ID [<015d3b8119c73f2291496f4b9d03fe4f>"
    "<015d3b8119c73f2291496f4b9d03fe4f>] >>\nstartxref\n399\n%%EOF"
)
