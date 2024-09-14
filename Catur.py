import pygame
import sys

pygame.init()
pygame.mixer.init()

info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h

WIDTH, HEIGHT = min(800, SCREEN_WIDTH), min(800, SCREEN_HEIGHT)

window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Catur")

move_sound = pygame.mixer.Sound('Catur/Sound/Move.wav')
capture_sound = pygame.mixer.Sound('Catur/Sound/Capture.wav')
gover_sound = pygame.mixer.Sound('Catur/Sound/Game_Over.wav')

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SQUARE_COLOR1 = (240, 218, 181)
SQUARE_COLOR2 = (180, 137, 100)
HIGHLIGHT_COLOR = (0, 203, 6)
MOVE_HIGHLIGHT_COLOR = (0, 203, 6) 
MOVE_EAT_HIGHLIGHTCOLOR = (187, 0, 0)

SQUARE_SIZE = WIDTH // 8
PIECE_SIZE = SQUARE_SIZE - 20

PIECE_IMAGES = {
    'white_pawn': pygame.transform.scale(pygame.image.load('Catur/Icon/white_pawn.png'), (PIECE_SIZE, PIECE_SIZE)),
    'white_rook': pygame.transform.scale(pygame.image.load('Catur/Icon/white_rook.png'), (PIECE_SIZE, PIECE_SIZE)),
    'white_knight': pygame.transform.scale(pygame.image.load('Catur/Icon/white_knight.png'), (PIECE_SIZE, PIECE_SIZE)),
    'white_bishop': pygame.transform.scale(pygame.image.load('Catur/Icon/white_bishop.png'), (PIECE_SIZE, PIECE_SIZE)),
    'white_queen': pygame.transform.scale(pygame.image.load('Catur/Icon/white_queen.png'), (PIECE_SIZE, PIECE_SIZE)),
    'white_king': pygame.transform.scale(pygame.image.load('Catur/Icon/white_king.png'), (PIECE_SIZE, PIECE_SIZE)),
    'black_pawn': pygame.transform.scale(pygame.image.load('Catur/Icon/black_pawn.png'), (PIECE_SIZE, PIECE_SIZE)),
    'black_rook': pygame.transform.scale(pygame.image.load('Catur/Icon/black_rook.png'), (PIECE_SIZE, PIECE_SIZE)),
    'black_knight': pygame.transform.scale(pygame.image.load('Catur/Icon/black_knight.png'), (PIECE_SIZE, PIECE_SIZE)),
    'black_bishop': pygame.transform.scale(pygame.image.load('Catur/Icon/black_bishop.png'), (PIECE_SIZE, PIECE_SIZE)),
    'black_queen': pygame.transform.scale(pygame.image.load('Catur/Icon/black_queen.png'), (PIECE_SIZE, PIECE_SIZE)),
    'black_king': pygame.transform.scale(pygame.image.load('Catur/Icon/black_king.png'), (PIECE_SIZE, PIECE_SIZE)),
}

INITIAL_POSITIONS = {
    'white': {
        'pawn': [(6, i) for i in range(8)],
        'rook': [(7, 0), (7, 7)],
        'knight': [(7, 1), (7, 6)],
        'bishop': [(7, 2), (7, 5)],
        'queen': [(7, 3)],
        'king': [(7, 4)]
    },
    'black': {
        'pawn': [(1, i) for i in range(8)],
        'rook': [(0, 0), (0, 7)],
        'knight': [(0, 1), (0, 6)],
        'bishop': [(0, 2), (0, 5)],
        'queen': [(0, 3)],
        'king': [(0, 4)]
    }
}

def draw_board():
    for row in range(8):
        for col in range(8):
            color = SQUARE_COLOR1 if (row + col) % 2 == 0 else SQUARE_COLOR2
            pygame.draw.rect(window, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(pieces):
    for color, piece_type in pieces.items():
        for piece, positions in piece_type.items():
            for row, col in positions:
                piece_name = f'{color}_{piece}'
                window.blit(PIECE_IMAGES[piece_name], (col * SQUARE_SIZE + 10, row * SQUARE_SIZE + 10))

def piece_at(pieces, row, col):
    for color, piece_type in pieces.items():
        for piece, positions in piece_type.items():
            if (row, col) in positions:
                return color, piece
    return None

def valid_moves(piece_type, start_row, start_col, pieces, turn):
    moves = []
    direction = 1 if turn == 'black' else -1

    def add_move(r, c):
        if 0 <= r < 8 and 0 <= c < 8:
            target = piece_at(pieces, r, c)
            if target is None or target[0] != turn:
                moves.append((r, c))

    if piece_type == 'pawn':
        forward_row = start_row + direction
        if piece_at(pieces, forward_row, start_col) is None:
            moves.append((forward_row, start_col)) 
            if (turn == 'white' and start_row == 6) or (turn == 'black' and start_row == 1):
                forward_two_rows = forward_row + direction
                if piece_at(pieces, forward_two_rows, start_col) is None:
                    moves.append((forward_two_rows, start_col))
        for dc in [-1, 1]:
            new_col = start_col + dc
            if 0 <= new_col < 8:
                target = piece_at(pieces, forward_row, new_col)
                if target and target[0] != turn:
                    moves.append((forward_row, new_col))

    elif piece_type == 'knight':
        knight_moves = [
            (start_row + 2, start_col + 1), (start_row + 2, start_col - 1),
            (start_row - 2, start_col + 1), (start_row - 2, start_col - 1),
            (start_row + 1, start_col + 2), (start_row + 1, start_col - 2),
            (start_row - 1, start_col + 2), (start_row - 1, start_col - 2)
        ]
        for r, c in knight_moves:
            add_move(r, c)

    elif piece_type in ['rook', 'bishop', 'queen']:
        directions = []
        if piece_type in ['rook', 'queen']:
            directions += [(1, 0), (-1, 0), (0, 1), (0, -1)]  
        if piece_type in ['bishop', 'queen']:
            directions += [(1, 1), (-1, -1), (1, -1), (-1, 1)]  

        for dr, dc in directions:
            r, c = start_row, start_col
            while True:
                r += dr
                c += dc
                if 0 <= r < 8 and 0 <= c < 8:
                    target = piece_at(pieces, r, c)
                    if target is None:
                        moves.append((r, c))
                    elif target[0] != turn:
                        moves.append((r, c))
                        break
                    else:
                        break 
                else:
                    break

    elif piece_type == 'king':
        king_moves = [
            (start_row + 1, start_col), (start_row - 1, start_col),
            (start_row, start_col + 1), (start_row, start_col - 1),
            (start_row + 1, start_col + 1), (start_row - 1, start_col - 1),
            (start_row + 1, start_col - 1), (start_row - 1, start_col + 1)
        ]
        for r, c in king_moves:
            add_move(r, c)

    return moves

def highlight_square(row, col, color, border_width=4):
    pygame.draw.rect(window, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), border_width)

def promote_pawn(color, row, col):
    options = ['Ratu', 'Benteng', 'Gajah', 'Kuda']  
    promotion_map = {
        'Ratu': 'queen',
        'Benteng': 'rook',
        'Gajah': 'bishop',
        'Kuda': 'knight'
    }

    font = pygame.font.Font(None, 36)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                index = y // 100
                if 0 <= index < 4:
                    return promotion_map[options[index]]

        window.fill(WHITE)
        for i, option in enumerate(options):
            text = font.render(option.capitalize(), True, BLACK)
            window.blit(text, (WIDTH // 2 - text.get_width() // 2, i * 100 + 50))

        pygame.display.flip()

def check_winner(pieces):
    white_king = pieces['white']['king']
    black_king = pieces['black']['king']
    
    if not white_king:
        return 'black'
    elif not black_king:
        return 'white'
    return None

def display_winner(winner):
    font = pygame.font.Font(None, 72)
    message = f"{'Putih' if winner == 'white' else 'Hitam'} Menang!"
    text = font.render(message, True, BLACK)

    blur_surface = pygame.Surface((WIDTH, HEIGHT))
    blur_surface.set_alpha(128)
    blur_surface.fill(WHITE)
    
    window.blit(blur_surface, (0, 0))
    window.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()

    pygame.time.wait(3000)

def reset_game():
    pieces = {'white': {}, 'black': {}}
    for color, piece_type in INITIAL_POSITIONS.items():
        for piece, positions in piece_type.items():
            pieces[color][piece] = positions.copy() 
    return pieces, 'white', None, []

def main():
    clock = pygame.time.Clock()

    pieces, turn, selected_piece, valid_moves_list = reset_game()

    while True:
        draw_board()
        draw_pieces(pieces)

        if selected_piece:
            start_row, start_col = selected_piece
            highlight_square(start_row, start_col, HIGHLIGHT_COLOR, border_width=4)
            
            for move_row, move_col in valid_moves_list:
                target = piece_at(pieces, move_row, move_col)
                if target and target[0] != turn:  
                    highlight_square(move_row, move_col, MOVE_EAT_HIGHLIGHTCOLOR, border_width=4)
                else:  
                    highlight_square(move_row, move_col, MOVE_HIGHLIGHT_COLOR, border_width=4)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                row, col = y // SQUARE_SIZE, x // SQUARE_SIZE
                clicked_piece = piece_at(pieces, row, col)

                if selected_piece:
                    if (row, col) in valid_moves_list:
                        color, piece = piece_at(pieces, selected_piece[0], selected_piece[1])
                        pieces[color][piece].remove(selected_piece)
                        move_sound.play()

                        target = piece_at(pieces, row, col)
                        if target and target[0] != turn:
                            target_color, target_piece = target
                            pieces[target_color][target_piece].remove((row, col))
                            
                            winner = check_winner(pieces)
                            if winner:
                                gover_sound.play()
                            elif not winner:
                                capture_sound.play()

                        pieces[color][piece].append((row, col))

                        if piece == 'pawn' and (row == 0 or row == 7):
                            if not winner:
                                promoted_piece = promote_pawn(turn, row, col)
                                pieces[color][piece].remove((row, col))

                                if promoted_piece:
                                    pieces[color][promoted_piece].append((row, col))

                        winner = check_winner(pieces)
                        if winner:
                            display_winner(winner)
                            pieces, turn, selected_piece, valid_moves_list = reset_game()

                        else:
                            turn = 'black' if turn == 'white' else 'white'

                    selected_piece = None
                    valid_moves_list = []

                elif clicked_piece and clicked_piece[0] == turn:
                    selected_piece = (row, col)
                    valid_moves_list = valid_moves(clicked_piece[1], row, col, pieces, turn)

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
