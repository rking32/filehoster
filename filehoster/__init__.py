#    This file is part of FileHoster.

#    FileHoster is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    FileHoster is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with FileHoster.  If not, see <https://www.gnu.org/licenses/>.


from .client import WebClient


app = WebClient(__name__)
webapp = app.get_start("0.0.0.0", port=8080)
